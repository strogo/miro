import sys
import objc
import QTKit
import AppKit
import Foundation

# =============================================================================

def extractDuration(qtmovie):
    qttime = qtmovie.duration()
    if qttime.timeScale == 0:
        return -1
    return int((qttime.timeValue / float(qttime.timeScale)) * 1000)

# -----------------------------------------------------------------------------

def extractThumbnail(qtmovie, target, width=0, height=0):
    try:
        qttime = qtmovie.duration()
        qttime.timeValue *= .5
        frame = qtmovie.frameImageAtTime_(qttime)
        if frame is objc.nil:
            return "Failure"

        frameSize = frame.size()
        if frameSize.width == 0 or frameSize.height == 0:
            return "Failure"

        if (width == 0) and (height == 0):
            width = frameSize.width
            height = frameSize.height

        frameRatio = frameSize.width / frameSize.height
        sourceSize = frame.size()
        sourceRatio = sourceSize.width / sourceSize.height
        destinationSize = Foundation.NSSize(width, height)
        destinationRatio = destinationSize.width / destinationSize.height

        if sourceRatio > destinationRatio:
            size = Foundation.NSSize(destinationSize.width, destinationSize.width / sourceRatio)
            pos = Foundation.NSPoint(0, (destinationSize.height - size.height) / 2.0)
        else:
            size = Foundation.NSSize(destinationSize.height * sourceRatio, destinationSize.height)
            pos = Foundation.NSPoint((destinationSize.width - size.width) / 2.0, 0)

        destination = AppKit.NSImage.alloc().initWithSize_(destinationSize)
        try:
            destination.lockFocus()
            AppKit.NSGraphicsContext.currentContext().setImageInterpolation_(AppKit.NSImageInterpolationHigh)
            AppKit.NSColor.blackColor().set()
            AppKit.NSRectFill(((0,0), destinationSize))
            frame.drawInRect_fromRect_operation_fraction_((pos, size), ((0,0), sourceSize), AppKit.NSCompositeSourceOver, 1.0)
        finally:
            destination.unlockFocus()

        tiffData = destination.TIFFRepresentation()
        imageRep = AppKit.NSBitmapImageRep.imageRepWithData_(tiffData)
        properties = {AppKit.NSImageCompressionFactor: 0.8}
        jpegData = imageRep.representationUsingType_properties_(AppKit.NSJPEGFileType, properties)
        jpegData = str(jpegData.bytes())
        if jpegData is None:
            return "Failure"

        output = file(target, 'wb')
        output.write(jpegData)
        output.close()
    except Exception, e:
        return "Failure"

    return "Success"

# =============================================================================

moviePath = sys.argv[1].decode('utf-8')
thumbPath = sys.argv[2].decode('utf-8')

info = AppKit.NSBundle.mainBundle().infoDictionary()
info["LSBackgroundOnly"] = "1"
AppKit.NSApplicationLoad()

(qtmovie, error) = QTKit.QTMovie.movieWithFile_error_(moviePath)
if qtmovie is None or error is not objc.nil:
    sys.exit(0)

duration = extractDuration(qtmovie)
print "Miro-Movie-Data-Length: %s" % duration

thmbResult = extractThumbnail(qtmovie, thumbPath)
print "Miro-Movie-Data-Thumbnail: %s" % thmbResult

sys.exit(0)

# =============================================================================
