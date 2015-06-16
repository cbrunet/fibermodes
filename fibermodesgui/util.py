
def clearLayout(layout, fromIndex=0):
    if layout is not None:
        while layout.count() > fromIndex:
            item = layout.takeAt(fromIndex)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clearLayout(item.layout())

