CLASS
  NAME "0 tot 20 km/h - snelweg"
  EXPRESSION ((([avg_speed] > 0) AND ([avg_speed] < 20)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 20) AND ([avg_speed] < 40)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 40) AND ([avg_speed] < 60)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 60) AND ([avg_speed] < 80)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 80) AND ([avg_speed] < 100)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 100) AND ([avg_speed] < 120)) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] >= 120) AND ([avg_speed] < 160)) AND ("[road_type]" = "H"))
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
  EXPRESSION (([avg_speed] >= 160) AND ("[road_type]" = "H"))
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
  EXPRESSION ((([avg_speed] > 0) AND ([avg_speed] < 10)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 10) AND ([avg_speed] < 20)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 20) AND ([avg_speed] < 30)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 30) AND ([avg_speed] < 40)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 40) AND ([avg_speed] < 50)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 50) AND ([avg_speed] < 60)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 60) AND ([avg_speed] < 80)) AND ("[road_type]" = "O"))
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
  EXPRESSION ((([avg_speed] >= 80) AND ([avg_speed] < 200)) AND ("[road_type]" = "O"))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#008C35"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END
