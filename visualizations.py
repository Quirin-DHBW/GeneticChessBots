import pandas as pd
import plotly.express as px

df = pd.read_csv("history.csv", sep=";")

def extract_weights(weight_str):
    weight_str = weight_str.strip("{}")
    weights = {}
    for pair in weight_str.split(","):
        key, value = pair.split(":")
        weights[key.strip().strip("'").strip('"')] = float(value)
    return weights

df['Weights Dict'] = df['Weights'].apply(extract_weights)

# And now make the dict into actual columns, so we can plot them more easily
weights_df = pd.json_normalize(df['Weights Dict'])
df = pd.concat([df, weights_df], axis=1)

# And now a plot showing the average weights (just as bars) of a generation, with a slider for the generations
fig = px.histogram(
    df,
    x=list(weights_df.columns),
    animation_frame="Generation",
    nbins=100)
fig.show()


