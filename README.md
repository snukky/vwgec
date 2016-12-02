GEC VW
======

Development in progress...


Workflow
--------

Given `train.txt`, `dev.m2`, and `test.m2`:

1. Train model
    1. Extract features from `train.txt` producing `train.feats` and `train.cwords`
    1. Train VW classifier on `train.feats` creating model `model.vw`
1. Tune threshold parameter
    1. Create file `dev.txt` with parallel sentences from `dev.m2`
    1. Extract features from `dev.txt` producing `dev.feats` and `dev.cwords`
    1. Run VW classifier on `dev.feats` and model `model.vw` producing `dev.pred`
    1. Perform grid search to find best threshold parameter
        1. Apply predictions `dev.thr.pred` into `dev.thr.out` using `dev.cwords`
        1. Run M2 scorer on `dev.thr.out`
1. Evaluate
    1. Create file `test.txt` with parallel sentences from `test.m2`
    1. Extract features from `test.txt` producing `test.feats` and `test.cwords`
    1. Run VW classifier on `test.feats` and model `model.vw` producing `test.pred`
    1. Apply predictions `test.pred` into `test.out` using `test.cwords`
    1. Run M2 scorer on `test.out`
