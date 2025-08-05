# Experimentation Process for Image Classification Model

## Overview

In this project, we developed a Convolutional Neural Network (CNN) using TensorFlow and Keras to classify images into predefined categories. Our model architecture consisted of three convolutional layers with increasing filter sizes, followed by a fully connected dense layer and a softmax output. The model also included a dropout layer to address overfitting.

## Experimentation Details

During the experimentation phase, we tried various combinations of layers and hyperparameters to improve the model's performance. Initially, we started with just two convolutional layers and a dense output. However, the model struggled to generalize well on the validation set, and we observed signs of overfitting — the training accuracy was significantly higher than the validation accuracy.

To improve feature extraction, we added a third convolutional layer (`Conv2D(128, (3, 3), activation='relu')`) and increased the filter depth progressively (32 → 64 → 128). This helped the model capture more complex patterns from the images and improved validation accuracy slightly.

We also experimented with different kernel sizes and pooling strategies but found the standard `(3, 3)` kernel and `(2, 2)` max pooling to work consistently well. One major improvement came from adding a `Dropout(0.5)` layer after the fully connected dense layer. Before dropout, the model was memorizing training data. After adding dropout, overfitting reduced significantly and the gap between training and validation accuracy narrowed, indicating better generalization.

## Observations

- Deeper networks improved learning but risked overfitting without dropout.
- Dropout with a 0.5 rate proved effective for regularization.
- Increasing the number of convolutional layers improved accuracy up to a point, beyond which the returns diminished.
- Model performance depended heavily on proper image resizing and preprocessing; uniform image dimensions helped stabilize training.

In conclusion, a balanced model with three convolutional layers, max pooling, a dense layer with dropout, and a softmax output yielded the best results in terms of both accuracy and generalization.
