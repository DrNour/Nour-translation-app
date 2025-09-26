from comet import download_model, load_from_checkpoint

model_path = download_model("Unbabel/wmt22-comet-da")
model = load_from_checkpoint(model_path)

def compute_comet(source: str, hypothesis: str, reference: str) -> float:
    data = [{"src": source, "mt": hypothesis, "ref": reference}]
    return model.predict(data, batch_size=8, gpus=0).scores[0]
