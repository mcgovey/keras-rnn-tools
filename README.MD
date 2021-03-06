# KerasTools
[![MIT Licence](https://badges.frapsoft.com/os/mit/mit.png?v=103)](https://opensource.org/licenses/mit-license.php)
[![mcgovey](https://circleci.com/gh/mcgovey/KerasTools.svg?style=shield)](https://github.com/mcgovey/kerastools)
[![codecov](https://codecov.io/gh/mcgovey/KerasTools/branch/master/graph/badge.svg)](https://codecov.io/gh/mcgovey/KerasTools)

This package contains helpful functions for preparing and understanding data output to be used in different Keras architectures.

## Features
!!Important: Currently only tools used for RNNs have been implemented for this project. Additional features described in the roadmap below are planned for addition. 
If you have suggestions please open an [Issue](https://github.com/mcgovey/KerasTools/issues) and flag it as an enhancement.

## Documentation
Full documentation can be found [here](https://kerastools.readthedocs.io/en/latest/api_docs.html).

## Remaining steps
- Finish predict_ts api
- Build predict_ts tests
- Create unscale api
- Build unscale tests
- Run through tests again and add where coverage is missing
- Update docs with full comments and examples
- Refactor readme page
- Submit to pypi

## Modules Under Development and Planned
- Universal prep
	- train_test_split: Function to create training and test data from different data sets
	- scale: minmax, standard, log, boxcox transformations to the data. Fit and transform train, transform test and validation only.
- RNNs
	- transform_for_rnn: Create time series data set (np arrays)
- CNNs
	- transform_for_cnn: Create np arrays
- Pre Model
	- get_input_shape: return input shape from training data for model
- Post Model
	- unscale: reverse scaling methods. User passes new array, gets back
	- ts_predictions: handle ts steps to predict for future
	- model_summary: Output model arch summary and 

## Become a sponsor to learn more
Web and video tutorials are available to those who are willing to become a sponsor. Visit my sponsor page to learn more.
