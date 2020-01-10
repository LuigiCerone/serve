import torch
from torch.autograd import Variable
from .text_handler import TextHandler
from torchtext.data.utils import ngrams_iterator


class TextClassifier(TextHandler):
    """
    TextClassifier handler class. This handler takes a text (string) and
    as input and returns the classification text based on the model vocabulary.
    """

    def __init__(self):
        super(TextClassifier, self).__init__()

    def preprocess(self, data):
        """
         Normalizes the input text for PyTorch model,
         returns an Numpy array
        """
        text = data[0].get("data")
        if text is None:
            text = data[0].get("body")

        text = text.decode('utf-8')

        ngrams = 2

        # remove html tags
        text = self._remove_html_tags(text)

        # Convert text to all lower case
        text = text.lower()

        # expand contractions [like I'd -> I would, don't -> do not]
        text = self._expand_conrtactions(text)

        # remove accented characters
        text = self._remove_accented_characters(text)

        # remove punctuations
        text = self._remove_puncutation(text)

        text = self._tokenize(text)

        text = torch.tensor([self.source_vocab[token] for token in ngrams_iterator(text, ngrams)])

        return text

    def inference(self, text):
        """
        Predict the class of a text using a trained deep learning model and vocabulary.
        """

        self.model.eval()
        inputs = Variable(text).to(self.device)
        output = self.model.forward(inputs, torch.tensor([0]))

        output = output.argmax(1).item() + 1

        if self.mapping:
            output = self.mapping[str(output)]

        return [output]

    def postprocess(self, inference_output):
        return inference_output


_service = TextClassifier()


def handle(data, context):
    try:
        if not _service.initialized:
            _service.initialize(context)

        if data is None:
            return None

        data = _service.preprocess(data)
        data = _service.inference(data)
        data = _service.postprocess(data)

        return data
    except Exception as e:
        raise e
