import pandas as pd
import numpy as np
# import sklearn
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split

#matplotlib
import matplotlib.pyplot as plt

# libraries used for train test split
import random
from math import floor
from types import SimpleNamespace

class keras_tools:
	def __init__(self, data:pd.DataFrame, \
					index = None,
					features:list = [],
					y_val = None,
					ts_n_y_vals:int = None,
					data_orientation:str = 'row',
					debug:bool = False):
		"""Setup the keras-rnn-tools helper class with passed variables
				
				Args:
					data (pd.DataFrame): base dataframe in pandas format.
					index (str or int): if data_orientation='row' then index number or column name that should be used as the index of the resulting dataframe,
						if data_orientation='column' then row index of row that should be used as index
					features(list): if data_orientation='row' then list of integer indices or column names of the columns that should be used as features,
						if data_orientation='column' then list of integer indices that should be used as features
					y_val (str or pd.DataFrame, optional): target variable index or column name, only used for non-timeseries problems.
					ts_n_y_vals (int): The number of y values to capture for each data set, only used for timeseries problems.
					data_orientation (string): string specifying whether the data frame that is passed will need to be pivoted or not ('row' or 'column', row gets transposed for time-series problems)
					debug (bool): indication of whether to output print values for debugging
		"""


		self.data = data
		self.debug = debug

		# check if y_val is populated
		if y_val is not None:
			
			self.y_val = y_val #TODO: add logic to split on y value
			
			if isinstance(y_val, str):
				print("passed y string")
			elif isinstance(y_val, pd.DataFrame):
				print("passed data frame")
				
		# check if ts_n_y_vals is populated
		elif ts_n_y_vals is not None:
			self.ts_n_y_vals = ts_n_y_vals
			if data_orientation == 'row':
				if self.debug == True: print("Row-wise orientation")
				# set index based on value passed
				if index == None:
					pass
				elif isinstance(index, int):
					self.data.index = self.data.iloc[:,index]
				elif isinstance(index, str):
					self.data.index = self.data[index]
				else:
					raise AttributeError(f"The index parameter passed ({index}) was not of type int or string")
				
				if all(isinstance(n, int) for n in features):
					print("all passed as integer")
					self.data = self.data.iloc[:,features]
				elif all(isinstance(n, str) for n in features):
					print("all passed as str")
				else:
					raise AttributeError(f"The features {features} were not consistently of type int or string")
				self.data = self.data.T
				if self.debug == True: print(self.data)
				
			elif data_orientation == 'column':
				if self.debug == True: print("Column-wise orientation")
			else:
				raise AttributeError(f"Type {data_orientation} specified is not valid. Must be either 'column' or 'row'")
		# if neither are populated then raise error
		else:
			raise AttributeError("Either y_val or ts_n_y_vals must be populated.")

		# other variables used
		self.scaler = "" # defined in scale()
		
		# split df data
		self.train_df = ""
		self.test_df = ""
		self.valid_df = ""
		
		# transformed data as np
		self.X_train = ""
		self.X_test = ""
		self.X_valid = ""
		self.y_train = ""
		self.y_test = ""
		self.y_valid = ""
		
		

	def _scale(self, 
				scaler = None,
				output_scaler:bool = False):
		"""Scale the data in the data set. Prescribe the same scaling to the test and validation data sets.
				
				Args:
					scaler (sklearn scaler or string, optional): optional scaling of data, passed as sklearn scaler or string of scaler type (minmax or standard).
					output_scaler (bool, optional): Include the fit scaler in the output. Default is False.
		"""
		
		self.scaler = scaler

		if isinstance(self.scaler, str):
			if self.debug == True: print("scaler string")
			if 'minmax' in self.scaler.lower():
				self.scaler = MinMaxScaler()

			elif 'standard' in self.scaler.lower():
				self.scaler = StandardScaler()
			else:
				raise AttributeError("Invalid Scaler Type Passed (minmax or standard expected)")
		elif self.scaler is not None:
			if self.debug == True: print("scaler passed")
		else:
			if self.debug == True: print("no scaler passed")
			raise AttributeError(f"Scaler type {scaler} was not sklearn scaler or string of ('minmax' or 'standard').")
			
		print(f"running for size {self.train_df.iloc[:,:-int(self.ts_n_y_vals)].shape}")
		
		# fit to training data
		self.scaler.fit(self.train_df.iloc[:,:-int(self.ts_n_y_vals)].T)
		
		# transform all the data in the data set
		print(self.train_df)
		self.train_df = pd.DataFrame(self.scaler.transform(self.train_df.T).T)
		print(self.train_df)
		# self.test_df = self.scaler.transform(self.test_df.T).T
		# self.valid_df = self.scaler.transform(self.valid_df.T).T
			
		if output_scaler: return self.scaler
		
		
	def _chunk_data (self, df, output_labels = True, **kwargs):
		"""Helper to split data into x and y based on the previously split data
				
			Args:
				df (object): Indication of the type of split to perform. Must be one of 'sequential', 'overlap', or 'sample'
				output_labels (bool, optional): indicator for whether y values also need to be outputted after chunking
				**kwargs: 
			Returns:

		"""
      

		# reassign the dictionary variables to variables in namespace for easy access
		n = SimpleNamespace(**kwargs)
		np_arr_list, y_arr_list = [], []
		
		
		end = df.shape[1]
		        
		# loop through each step and create a new np array to add to list
		for chunk_start in range(0, (end - n.sample_size - n.y_size + 1), n.step):
		    
		    # get a chunk of x values and store to array
		    if self.debug == True: print("From {} to {}".format(chunk_start, chunk_start + n.sample_size))
		    np_chunk = np.array(df.iloc[:,(chunk_start):(chunk_start + n.sample_size)])
		    # add stored array to list
		    np_arr_list.append(np_chunk)
		    
		    if output_labels:
		        if self.debug == True: print("Y samples from {} to {}".format((chunk_start + n.sample_size), (chunk_start + n.sample_size + n.y_size)))
		        y_df_chunk = df.iloc[:,(chunk_start + n.sample_size):(chunk_start + n.sample_size + n.y_size)]
		        y_np_chunk = np.array(y_df_chunk)
		        y_arr_list.append(y_np_chunk)
		
		# stack all the x samples together
		np_stacked_chunks = np.stack(np_arr_list)
		x_reshaped = np.transpose(np_stacked_chunks, (0,2,1))
		
		if output_labels:
		    # stack all the y samples together
		    y_np_stacked_chunks = np.stack(y_arr_list)
		    y_reshaped = y_np_stacked_chunks
		    return x_reshaped, y_reshaped
		else:
		    return x_reshaped

	def train_test_split(self, 
										split_type:str = 'sample',
										split_pct:float = 0.3,
										val_split_pct:float = 0.1,
										fill_na:bool = True,
										return_df:bool = False):
		"""Create the base train-test-validation split for time-series data
				
			Args:
				split_type (str): Indication of the type of split to perform. Must be one of 'sequential', 'overlap', or 'sample'
				split_pct (bool): 
				val_split_pct (bool, optional): 
				fill_na (bool): Replace all NAs with 0's, typical prep. Default is True.
				return_df (bool): Option to instead return the data as a dataframe (useful for debugging). Default is False.
			Returns:

		"""
		#### basic parameter checking
		if split_pct < 0 or split_pct > 1:
			raise AttributeError(f"split_pct must be between 0 and 1. {split_pct} passed.") 
		if val_split_pct < 0 or val_split_pct > 1:
			raise AttributeError(f"val_split_pct must be between 0 and 1. {val_split_pct} passed.") 

		if fill_na==True:
			self.data.fillna(0, inplace=True)

		#### create split depending on split_type
		if split_type == 'sequential':
			if self.debug == True: print("sequential split")
			
			train_test_split_num = floor(self.data.shape[1] * (1 - split_pct - val_split_pct))
			test_val_split = floor(self.data.shape[1] * (1 - val_split_pct))
			if self.debug == True: print("Split at {} and {}".format(train_test_split_num, test_val_split))

			# print(self.data, train_test_split_num)
			
			self.train_df = np.array(self.data.iloc[:, 0:train_test_split_num])
			self.test_df = np.array(self.data.iloc[:, train_test_split_num:test_val_split])
			
			if self.debug: print(f"train_df: {self.train_df}")
			
			if val_split_pct > 0 and val_split_pct < 1:
				# create validation variables
				x_val_start = test_val_split
				x_val_end = self.data.shape[1] - self.ts_n_y_vals
				
				self.valid_df = np.array(self.data.iloc[:, test_val_split:])
				if return_df: return self.train_df, self.test_df, self.valid_df
			else:
				if return_df: return self.train_df, self.test_df
			 
			
		elif split_type == 'overlap':
			if self.debug == True: print("overlap split")
			
			
			train_test_split_num = floor((self.data.shape[1] - self.ts_n_y_vals) * (1 - split_pct - val_split_pct))
			test_val_split = floor((self.data.shape[1] - self.ts_n_y_vals) * (1 - val_split_pct))
			
			# self._split_dfs()
			
			self.train_df = self.data.iloc[:, 0:(train_test_split_num + self.ts_n_y_vals)]
			self.test_df = self.data.iloc[:, (train_test_split_num):(test_val_split + self.ts_n_y_vals)]
			
			if val_split_pct > 0 and val_split_pct < 1:
				# create validation variables
				x_val_start = test_val_split
				x_val_end = self.data.shape[1] - self.ts_n_y_vals
				
				self.valid_df = self.data.iloc[:, test_val_split:]
				if return_df: return self.train_df, self.test_df, self.valid_df
			else:
				if return_df: return self.train_df, self.test_df
				
				
		elif split_type == 'sample':
			if self.debug == True: print("sample split")
			
			# try to split by y_val first, move on if it's not set
			try:
				X_train, X_test, y_train, y_test = train_test_split(self.data, self.y_val, test_size=split_pct)
				X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_split_pct/(1-split_pct))
			except AttributeError:
				# for time-series this method only works if you want to sample specific features and keep the full time-series
				
				# split out test_df then remove rows from train_df
				self.test_df = self.data.loc[self.data.sample(frac=split_pct, replace=False).index]
				self.train_df = self.data.loc[~self.data.index.isin(self.test_df.index)]
				
				# split out valid_df then remove the rows from train_df
				self.valid_df = self.train_df.loc[self.train_df.sample(frac=val_split_pct, replace=False).index]
				self.train_df = self.train_df.loc[~self.train_df.index.isin(self.valid_df.index)]
				
				if val_split_pct > 0 and val_split_pct < 1:
					if return_df: return self.train_df, self.test_df, self.valid_df
				else:
					if return_df: return self.train_df, self.test_df
					
			return self.X_train
		else:
			raise AttributeError(f"Type {split_type} specified is not valid")
		if self.debug == True: print(self.data)
	
	def reshape_ts(self,
					step:int = 1,
					sample_size:int = 1, 
					scaler = None,
					output_scaler:bool = False):
		"""Transforms split data into format needed for RNN, optionally can scale the data as well.
				
			Args:
				step (int): The number of steps before you take another sample (e.g. [1,3,5,6,7,9] and step of 2 would return x values of [[1,3][5,6][7,9]])
				sample_size (int): The number of samples you want to take for each value (e.g. [1,3,5,6,7,9] and sample_size of 3 would return x values of [[1,3,5][3,5,6][5,6,7][6,7,9]])
				input_data (tuple of object, optional): if train/test/validation data was not split using the class, data can be added directly here.
				return_as_df (bool): Option to instead return the data as a dataframe (useful for debugging). Default is False.
				scaler (sklearn scaler or string, optional): optional scaling of data, passed as sklearn scaler or string of scaler type (minmax or standard).
				output_scaler (bool, optional): Include the fit scaler in the output. Default is False.
			Returns:
				scaler (object): If output_scaler==True then the fit scaler used will be returned.
		"""
		if scaler != None:
			self._scale(scaler = scaler, output_scaler = output_scaler)
		x_reshaped, y_reshaped = self._chunk_data(self.train_df, step = step, sample_size = sample_size, y_size = self.ts_n_y_vals)
		
		# get test data
		x_reshaped_test, y_reshaped_test = self._chunk_data(self.test_df, step = step, sample_size = sample_size, y_size = self.ts_n_y_vals)
		
		
		self.X_train = x_reshaped
		self.y_train = y_reshaped
		self.X_test = x_reshaped_test
		self.y_test = y_reshaped_test
		
		if len(self.valid_df)>1:
			# create val data sets
			x_reshaped_val, y_reshaped_val = self._chunk_data(self.valid_df, step = step, sample_size = sample_size, y_size = self.ts_n_y_vals)
			
			self.X_valid = x_reshaped_val
			self.y_valid = y_reshaped_val
			
		if output_scaler == True:
			return self.scaler

	def get_input_shape(self):
		return self.X_train.shape[1:3]

	def unscale(self,
					prediction_arr:object):
		"""Given an array, unscales the data back to original numeric scale
		
		Args:
			prediction_arr (object): 2D array of variables to be unscaled (if array is 3D from predictions, use shape_predictions() first)
		"""
		pass
	
	def predict_ts(self, 
					x_values, 
					y_values:object = None, 
					model:object = None,
					predict_shape:str = '2d'):
		"""Generates predictions from model for given x input
		
		Args:
			x_values (): 
			y_values (object): np.array of actuals if comparing values to actuals
			model (object): object of Keras model, can be optional if a model has been passed in previous method
			predict_shape (str): string indicator or '2d' or '3d' indicating how final layer of model is structured. See docs for more information.
			
		Returns:
			pred_list, actual_list (tuple of lists): Returns a list of predictions (returns a tuple of lists if y_values are provided for validation as well)
		"""
		
		predict_shape = predict_shape.lower()
		pred_list = []
		if y_values is not None: actual_list = y_values[:,:,0]
		
		# predict future weeks
		pred_list = self._train_iterative_preds(x_values, model)
		
		# print('train predict {} and actual shape {}'.format(np.asarray(pred_list)[:,:,0].shape, np.asarray(actual_list).shape))
		
		pred_list = self._reshape_pred_lists(np.asarray(pred_list)[:,:,0], 'preds', date_first=True)
		if y_values is not None: 
			actual_list = self._reshape_pred_lists(actual_list, 'actuals', date_first=True)
			return pred_list, actual_list
		
		else:
			return pred_list
			
	def _reshape_pred_lists (self, pred_list, column_name, date_first=True):
		"""Generates predictions from model for given x input
		
		Args:
		
		"""
		# reshape data
		pred_list = np.asarray(pred_list)
		pred_list = np.stack(pred_list)
		if pred_list.ndim == 3:
		    pred_list = pd.DataFrame(pred_list[0,:,:])
		else:
		    pred_list = pd.DataFrame(pred_list)
		pred_list = pd.DataFrame(pred_list.T)
		
		pred_list = pd.DataFrame(pred_list.stack())
		pred_list.reset_index(inplace=True)
		if date_first == True:
		    pred_list.columns = ['SKU_idx', 'DATE_idx', column_name]
		else:
		    pred_list.columns = ['DATE_idx', 'SKU_idx', column_name]
		    
		# rescale and exponentiate the data
		# pred_list.loc[:,column_name] = scaler.inverse_transform(pd.DataFrame(pred_list.loc[:,column_name]))
		# pred_list.loc[:,column_name] = pred_list.loc[:,column_name].apply(np.exp)
		# pred_list.loc[:,column_name] = pred_list.loc[:,column_name].fillna(0)
		
		return pred_list

	def _train_iterative_preds (self, x_train, model):
		"""
		
		"""
		pred_list2 = []
		
		if isinstance(x_train,(list)):
			for i in range(x_train[0].shape[0]):
				batch = x_train[0][i,:,:].reshape(1, x_train[0].shape[1], x_train[0].shape[2])
				batch2 = x_train[1][i,:,:].reshape(1, x_train[1].shape[1], x_train[1].shape[2])
				pred_list2.append(model.predict([batch, batch2])[0])
		else:
			for i in range(x_train.shape[0]):
				batch = x_train[i,:,:].reshape(1, x_train.shape[1], x_train.shape[2])
				pred_list2.append(model.predict(batch)[0])
		
		return pred_list2
	    
	 
	def model_summary(self, 
						model:object, 
						history:object = None, 
						show_charts:bool = True):
		# function for verifying results
		"""Transforms split data into format needed for RNN, optionally can scale the data as well.
				
			Args:
				model (object): Saved model of TensorFlow or Keras object
				history (object, optional): History from training model.fit
				show_charts (bool): Flag to decide if charts should be outputted
			Returns:

		"""
		self.model = model
		self.history = history
		
		print(model.summary())
		
		if show_charts:
			if history == None:
				raise AttributeError("'history' attribute missing in method call. Pass stored values of model.fit.")
			else:
				test_metrics, val_metrics = {}, {}
				num_metrics = 0
				
				# seperate test metrics from validation metrics
				for key, val in history.history.items():
					if key[:4] != 'val_':
						test_metrics[key] = val
						num_metrics += 1
					else:
						val_metrics[key] = val
				
				
				# plot performance curves
				plt.figure();
				fig, axes = plt.subplots(nrows=1, ncols=num_metrics, figsize=(12, 7))
				
				chart_idx = 0
				# loop through all test metrics, look for validation metrics as well and plot to charts
				for key, val in test_metrics.items():
					axes[chart_idx].plot(val, label = key)
					val_name = "".join(['val_',key])
					if val_name in val_metrics:
						axes[chart_idx].plot(val_metrics[val_name], label = val_name)
					axes[chart_idx].legend()
					chart_idx += 1
				
				# output to file if debugging
				if self.debug == True: fig.savefig('test_data/sample_chart.png')
				# try to show plot
				plt.show()

	def ts_transform(self, 
						split_type:str = 'sample',
						split_pct:float = 0.3,
						val_split_pct:float = 0.1,
						fill_na:bool = True,
						step:int = 1,
						sample_size:int = 1, 
						scaler = None,
						output_scaler:bool = False,
						return_df:bool = False):
		"""Combines methods to create a full data set preppossing for time-series problems
				
			Args:
				
			Returns:

		"""
		
		# run train-test split
		self.train_test_split(split_type='overlap',
										split_pct = split_pct,
										val_split_pct = val_split_pct)
		
		# run reshape
		self.reshape_ts(step = step,
										sample_size = sample_size)