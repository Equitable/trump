import tsadisplay as sad
import trump.orm as model

from subprocess import call

desc = sad.describe([getattr(model, attr) for attr in dir(model)])
colors = {'ncolor' : "lightgray", 'pcolor' : 'Salmon', 'mcolor' : 'lightblue', 'ccolor' : 'SpringGreen'}
open('schema.dot', 'w').write(sad.dot(desc, colors))
call(["dot", "-Tpng", "schema.dot", "-o", "schema.png"])

