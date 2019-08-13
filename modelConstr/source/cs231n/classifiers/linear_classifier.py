import numpy as np
from cs231n.classifiers.linear_svm import *
from cs231n.classifiers.softmax import *
import time

class LinearClassifier(object):

  def __init__(self):
    self.W = None

  def train(self, X, y, learning_rate=1e-3, reg=1e-5, num_iters=100,
            batch_size=200, verbose=False):
    """
    Train this linear classifier using stochastic gradient descent.

    Inputs:
    - X: A numpy array of shape (N, D) containing training data; there are N
      training samples each of dimension D.
    - y: A numpy array of shape (N,) containing training labels; y[i] = c
      means that X[i] has label 0 <= c < C for C classes.
    - learning_rate: (float) learning rate for optimization.
    - reg: (float) regularization strength.
    - num_iters: (integer) number of steps to take when optimizing
    - batch_size: (integer) number of training examples to use at each step.
    - verbose: (boolean) If true, print progress during optimization.

    Outputs:
    A list containing the value of the loss function at each training iteration.
    """
    
    num_train, dim = X.shape
    num_classes = np.max(y) + 1 # assume y takes values 0...K-1 where K is number of classes
    if self.W is None:
      # lazily initialize W
      print("W not initialized!")
      self.W = 0.001 * np.random.randn(dim, num_classes)

    # Run stochastic gradient descent to optimize W
    loss_history = []
    for it in range(num_iters):
      
      sample_indices = np.random.choice(np.arange(num_train), batch_size)
      X_batch = X[sample_indices]
      y_batch = y[sample_indices]

      # evaluate loss and gradient
      loss, grad = self.loss(X_batch, y_batch, reg)
      loss_history.append(loss)

      # perform parameter update
      # Update the weights using the gradient and the learning rate.          #
      self.W += -learning_rate * grad

      if verbose and it % 100 == 0:
        print('iteration %d / %d: loss %f' % (it, num_iters, loss))

    return loss_history

  def adaptive_train(self, X, y, hyper_params=[(1e-3,1e-5,200)], num_iters=1000, 
                     verbose=False):
    """
    Train this linear classifier using stochastic gradient descent.

    Inputs:
    - X: A numpy array of shape (N, D) containing training data; there are N
      training samples each of dimension D.
    - y: A numpy array of shape (N,) containing training labels; y[i] = c
      means that X[i] has label 0 <= c < C for C classes.
    - hyper_params comprises of:
        - learning_rate: (float) learning rate for optimization.
        - reg: (float) regularization strength.
        - batch_size: (integer) number of training examples to use at each step.
    - num_iters: (integer) number of steps to take when optimizing
    - verbose: (boolean) If true, print execution time of each iteration.

    Outputs:
    A list containing the value of the loss function at each training iteration.
    """
    
    num_train, dim = X.shape
    num_classes = np.max(y) + 1 # assume y takes values 0...K-1 where K is number of classes
    if self.W is None:
      # lazily initialize W
      self.W = 0.001 * np.random.randn(dim, num_classes)

    # Run stochastic gradient descent to optimize W
    loss_history = []
    batch_iters = int(num_iters/len(hyper_params))
    for learning_rate, reg, batch_size in hyper_params:
        if verbose:
            print('learning rate: %f, reg: %f, batch_size: %d' % 
                  (learning_rate, reg, batch_size))
            
        for it in range(batch_iters):
          tic = time.time()

          sample_indices = np.random.choice(np.arange(num_train), batch_size)
          X_batch = X[sample_indices]
          y_batch = y[sample_indices]

          # evaluate loss and gradient
          loss, grad = self.loss(X_batch, y_batch, reg)
          loss_history.append(loss)

          # Update the weights using the gradient and the learning rate.          #
          self.W += -learning_rate * grad

          toc = time.time()
          if verbose:
              print('Iteration #: %d, Exec time: %f s' % (it, (toc-tic)))
    return loss_history


  def predict(self, X):
    """
    Use the trained weights of this linear classifier to predict labels for
    data points.

    Inputs:
    - X: D x N array of training data. Each column is a D-dimensional point.

    Returns:
    - y_pred: Predicted labels for the data in X. y_pred is a 1-dimensional
      array of length N, and each element is an integer giving the predicted
      class.
    """
    y_pred = np.argmax(X.dot(self.W), axis=1)
    return y_pred
  
  def loss(self, X_batch, y_batch, reg):
    """
    Compute the loss function and its derivative. 
    Subclasses will override this.

    Inputs:
    - X_batch: A numpy array of shape (N, D) containing a minibatch of N
      data points; each point has dimension D.
    - y_batch: A numpy array of shape (N,) containing labels for the minibatch.
    - reg: (float) regularization strength.

    Returns: A tuple containing:
    - loss as a single float
    - gradient with respect to self.W; an array of the same shape as W
    """
    pass


class LinearSVM(LinearClassifier):
  """ A subclass that uses the Multiclass SVM loss function """

  def loss(self, X_batch, y_batch, reg):
    return svm_loss_vectorized(self.W, X_batch, y_batch, reg)


class Softmax(LinearClassifier):
  """ A subclass that uses the Softmax + Cross-entropy loss function """

  def loss(self, X_batch, y_batch, reg):
    return softmax_loss_vectorized(self.W, X_batch, y_batch, reg)
