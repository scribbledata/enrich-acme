import os
import sys
import numpy as np 
import pandas as pd 
from enrichsdk import Compute, S3Mixin
from datetime import datetime 
import logging 

import tensorflow as tf

logger = logging.getLogger("app") 

class MyTFTutorial(Compute, S3Mixin): 

    def __init__(self, *args, **kwargs): 
        super(MyTFTutorial,self).__init__(*args, **kwargs) 
        self.name = "TFTutorial" 

        self.testdata = { 
	    'conf': {
	        'args': {
		}
	    },
            'data': { 
            }
        }
    def process(self, state): 
        """
        Run the computation and update the state 
        """
        logger.debug("{} - process".format(self.name),
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))


        mnist = tf.keras.datasets.mnist

        
        (x_train, y_train),(x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        logger.debug("Loaded MNIST data",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))
        
        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(512, activation=tf.nn.relu),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation=tf.nn.softmax)
        ])
        logger.debug("Completed training ",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        

        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])
        logger.debug("Compiled with ADAM optimized",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))

        logger.debug("Starting FIT",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        
        model.fit(x_train, y_train, epochs=5,verbose=0)
        logger.debug("Completed FIT",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        

        logger.debug("Starting evaluate",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        
        model.evaluate(x_test, y_test, verbose=0)
        logger.debug("Completed evaluate",
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        
        

        logger.debug("{} - Completed".format(self.name),
                     extra=self.config.get_extra({
                         'transform': self.name 
                     }))        
        ###########################################
        # => Return 
        ###########################################
        return state 

    def validate_results(self, what, state): 
        """
        Check to make sure that the execution completed correctly
        """
        pass
    
        
provider = MyTFTutorial 
