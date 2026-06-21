import gradio as gr
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

LABELS = {0: "analysis", 1: "anecdote", 2: "explanation", 3: "hot_take"}

tokenizer = AutoTokenizer.from_pretrained(".")
model = AutoModelForSequenceClassification.from_pretrained(".").eval()


def classify(text: str):
    if not text.strip():
        return {label: 0.0 for label in LABELS.values()}
    inputs = tokenizer(text, truncation=True, max_length=256, return_tensors="pt")
    with torch.no_grad():
        probs = F.softmax(model(**inputs).logits, dim=-1)[0].numpy()
    return {LABELS[i]: float(probs[i]) for i in range(len(LABELS))}


demo = gr.Interface(
    fn=classify,
    inputs=gr.Textbox(
        lines=8,
        placeholder="Paste a Hacker News post or comment here...",
        label="Post text",
    ),
    outputs=gr.Label(num_top_classes=4, label="Predicted label and confidence"),
    title="TakeMeter",
    description=(
        "Classify a Hacker News post by rhetorical structure: "
        "**analysis** (evidence-backed), **explanation** (neutral mechanism), "
        "**anecdote** (personal experience), or **hot_take** (unsupported opinion). "
        "Fine-tuned DistilBERT on ~200 hand-labeled HN posts about databases."
    ),
    examples=[
        ["It took 5 years from construction start to grid connection for Oskarshamn R3, at the time the reactor with the world's highest rated output. Since it began operating it has produced 350TWh. That nuclear power must take forever is a myth and is only due to dysfunctional politics."],
        ["This morning, our database flagged a duplicate UUID (v4). The system inserted a new document with a fresh UUIDv4 and it came up with the exact same one as an existing record. The database only has about 15,000 records. Statistically impossible. Has that ever happened to anyone?"],
        ["They seem similar at a glance but they're quite different. You can think of SQLite as a transactional database while DuckDB is better used as an analytical database. SQLite is your metadata record, DuckDB is your ingestion/scanning/aggregating/joining engine."],
        ["Writing to disk for every write is required, otherwise you're not durable. Sure it's faster to never write to disk, then you reboot and you've lost data. /dev/null is a webscale database that is even faster!"],
    ],
    allow_flagging="never",
)

if __name__ == "__main__":
    demo.launch()
