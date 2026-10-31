import io,json,importlib.metadata as m
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import jupytext,nbformat
import panel as pn,plotly.graph_objects as go,bokeh.plotting as bp,ipywidgets,ipympl
x=np.arange(10.);df=pd.DataFrame({'x':x,'y':x*x});assert df.y.sum()==285
fig,ax=plt.subplots();ax.plot(x,df.y);buf=io.BytesIO();fig.savefig(buf,format='png');assert buf.getvalue().startswith(b'\x89PNG');plt.close(fig)
assert len(go.Figure(go.Scatter(x=x,y=x*x)).to_json())>100
p=bp.figure();p.line(x,x*x);assert p.renderers
assert pn.pane.DataFrame(df).object.equals(df)
assert ipywidgets.IntSlider(value=3).value==3
nb=nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell("print('paired-science')")]);text=jupytext.writes(nb,fmt='py:percent');restored=jupytext.reads(text,fmt='py:percent');assert restored.cells[0].source==nb.cells[0].source
print(json.dumps({'passed':True,'matplotlib_png_bytes':len(buf.getvalue()),'versions':{n:m.version(n) for n in ['numpy','pandas','matplotlib','panel','plotly','bokeh','ipympl','ipywidgets','pixi-kernel','jupytext']}}))
