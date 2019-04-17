CLASS
  NAME "0 tot 10 km/h"
  EXPRESSION (([avg_speed] > 0) AND ([avg_speed] < 10))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#EC0000"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 90   
  END
END

CLASS
  NAME "10 tot 20 km/h"
  EXPRESSION (([avg_speed] >= 10) AND ([avg_speed] < 20))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#FF9100"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 80   
  END
END

CLASS
  NAME "20 tot 30 km/h"
  EXPRESSION (([avg_speed] >= 20) AND ([avg_speed] < 30))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#FFE600"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 70   
  END
END

CLASS
  NAME "30 tot 40 km/h"
  EXPRESSION (([avg_speed] >= 30) AND ([avg_speed] < 40))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#BED200"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 60   
  END
END

CLASS
  NAME "40 tot 50 km/h"
  EXPRESSION (([avg_speed] >= 40) AND ([avg_speed] < 50))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#5FD25A"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "50 tot 60 km/h"
  EXPRESSION (([avg_speed] >= 50) AND ([avg_speed] < 60))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#01AF14"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "meer dan 60 km/h"
  EXPRESSION (([avg_speed] >= 60) AND ([avg_speed] < 80))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#008C35"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END

CLASS
  NAME "meer dan 80 km/h"
  EXPRESSION (([avg_speed] >= 80) AND ([avg_speed] < 200))
  STYLE
    WIDTH 3
    OUTLINECOLOR "#008C35"
    LINECAP BUTT
    LINEJOIN MITER
  OPACITY 50   
  END
END
