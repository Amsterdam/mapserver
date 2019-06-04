VALIDATION
   # %date% substitutions can only have letters, digits and underscore
   'default_date' '2019-04-03' 
   'date'     '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'

   # %bucket% substitutions can only be 1, 2 or 3 that translates to: morning rushhour, evening rushhour and rest of day respectively.
   'default_bucket' '1'
   'bucket'     '[1-3]'
END  

