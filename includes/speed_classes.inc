CLASS
  NAME "0 tot 20 km/h - snelweg"
  EXPRESSION ((([velocity] > 0) AND ([velocity] < 20)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#EC0000"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 90   
  END
END

CLASS
  NAME "20 tot 40 km/h - snelweg"
  EXPRESSION ((([velocity] >= 20) AND ([velocity] < 40)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#FF9100"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 80   
  END
END

CLASS
  NAME "40 tot 60 km/h - snelweg"
  EXPRESSION ((([velocity] >= 40) AND ([velocity] < 60)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#FFE600"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 70   
  END
END

CLASS
  NAME "60 tot 80 km/h - snelweg"
  EXPRESSION ((([velocity] >= 60) AND ([velocity] < 80)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#BED200"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 60   
  END
END

CLASS
  NAME "80 tot 100 km/h - snelweg"
  EXPRESSION ((([velocity] >= 80) AND ([velocity] < 100)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#5FD25A"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "100 tot 120 km/h - snelweg"
  EXPRESSION ((([velocity] >= 100) AND ([velocity] < 120)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#08C700"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "120 tot 160 km/h - snelweg"
  EXPRESSION ((([velocity] >= 120) AND ([velocity] < 160)) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#01AF14"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "meer dan 160 km/h - snelweg"
  EXPRESSION (([velocity] >= 160) AND ("[road_type]" = "H"))
  STYLE
    WIDTH 10
    OUTLINECOLOR "#FF00FF"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "0 tot 10 km/h - weg"
  EXPRESSION ((([velocity] > 0) AND ([velocity] < 10)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#EC0000"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 90   
  END
END

CLASS
  NAME "10 tot 20 km/h - weg"
  EXPRESSION ((([velocity] >= 10) AND ([velocity] < 20)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#FF9100"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 80   
  END
END

CLASS
  NAME "20 tot 30 km/h - weg"
  EXPRESSION ((([velocity] >= 20) AND ([velocity] < 30)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#FFE600"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 70   
  END
END

CLASS
  NAME "30 tot 40 km/h - weg"
  EXPRESSION ((([velocity] >= 30) AND ([velocity] < 40)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#BED200"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 60   
  END
END

CLASS
  NAME "40 tot 50 km/h - weg"
  EXPRESSION ((([velocity] >= 40) AND ([velocity] < 50)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#5FD25A"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "50 tot 60 km/h - weg"
  EXPRESSION ((([velocity] >= 50) AND ([velocity] < 60)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#01AF14"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "meer dan 60 km/h - weg"
  EXPRESSION ((([velocity] >= 60) AND ([velocity] < 80)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#008C35"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "meer dan 80 km/h - weg"
  EXPRESSION ((([velocity] >= 80) AND ([velocity] < 200)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#008C35"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END
