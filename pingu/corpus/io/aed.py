import os
import glob
import re

import pingu
from pingu.corpus import assets
from pingu.corpus import subset
from . import base

LABEL_PATTERN = re.compile(r'(.*)_\d')


class AEDReader(base.CorpusReader):
    """
    Reader for the Acoustic Event Dataset.

    .. seealso::

       `AED <https://data.vision.ee.ethz.ch/cvl/ae_dataset/>`_
          Download page
    """

    @classmethod
    def type(cls):
        return 'aed'

    def _check_for_missing_files(self, path):
        return []

    def _load(self, path):
        corpus = pingu.Corpus(path=path)

        test_folder = os.path.join(path, 'test')
        train_folder = os.path.join(path, 'train')

        test_utterance_ids = AEDReader.load_folder(test_folder, corpus)
        train_utterance_ids = AEDReader.load_folder(train_folder, corpus)

        test_filter = subset.MatchingUtteranceIdxFilter(utterance_idxs=test_utterance_ids)
        train_filter = subset.MatchingUtteranceIdxFilter(utterance_idxs=train_utterance_ids)

        test_subset = subset.Subview(corpus, filter_criteria=[test_filter])
        train_subset = subset.Subview(corpus, filter_criteria=[train_filter])

        corpus.import_subview('test', test_subset)
        corpus.import_subview('train', train_subset)

        return corpus

    @staticmethod
    def load_folder(path, corpus):
        utterance_ids = set()

        for wav_path in glob.glob(os.path.join(path, '**/*.wav'), recursive=True):
            basename = os.path.splitext(os.path.basename(wav_path))[0]

            match = LABEL_PATTERN.match(basename)

            if match is not None:
                label = match.group(1)

                corpus.new_file(wav_path, basename)
                utt = corpus.new_utterance(basename, basename)
                utt.set_label_list(assets.LabelList(idx='default', labels=[
                    assets.Label(label)
                ]))

                utterance_ids.add(basename)

        return utterance_ids
