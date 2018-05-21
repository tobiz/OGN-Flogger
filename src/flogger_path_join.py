import os

def path_join(path_name, file_names):
#    print "path: name: ", path_name
#   print "file_names: ", file_names
    ffn = path_name
    for name in file_names:
#        print "ffn: ", ffn
        ffn = os.path.join(ffn, name)
    return ffn

def path_join_dd(path_name, file_names):
    #
    # This produces: path_name/../fn1/fn2 etc when file_names is [fn1,fn2]
    #
#    print "path: name: ", path_name
#   print "file_names: ", file_names
#    p1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
    path_name = os.path.join(os.path.dirname(path_name), os.pardir)
    ffn = path_name
    for name in file_names:
#        print "ffn: ", ffn
        ffn = os.path.join(ffn, name)
    return ffn

