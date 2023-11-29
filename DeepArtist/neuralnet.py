import torch
import torchvision
import torchvision.transforms.v2 as transforms
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from matplotlib import pyplot as plt
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from preprocess import ImageDataManager

'''
In this file you will write end-to-end code to train a neural network to categorize fashion-mnist data
'''


'''
PART 1:
Preprocess the fashion mnist dataset and determine a good batch size for the dataset.
Anything that works is accepted.
'''

transform = transforms.Compose([
    transforms.ToImage(),
    transforms.Resize((224, 224), antialias=True),  # Explicitly set antialias to True
    transforms.ToDtype(torch.float32, scale=True),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # Adjust if images are grayscale
])

'''
PART 2:
Load the dataset. Make sure to utilize the transform and batch_size you wrote in the last section.
'''

BATCH_SIZE = 64
SQUARE_IMAGE_SIZE = 100

idm = ImageDataManager(data_root='./Data', square_image_size=SQUARE_IMAGE_SIZE)

(
    train_loader, validate_loader, test_loader
) = idm.split_loaders(train_split=0.8, validate_split=0.1, batch_size=BATCH_SIZE, random_seed=1)


'''
PART 3:
Design a multi layer perceptron. Since this is a purely Feedforward network, you mustn't use any convolutional layers
Do not directly import or copy any existing models.
'''


# define CNN for a 3-class problem with input size 160x160 images
class Net(nn.Module):

    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv4 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv5 = nn.Conv2d(128, 256, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(256 * 3 * 3, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 5)
        self.relu = nn.ReLU()
        self.final_activation = nn.LogSoftmax(dim=1)
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = self.pool(self.relu(self.conv3(x)))
        x = self.pool(self.relu(self.conv4(x)))
        x = self.pool(self.relu(self.conv5(x)))
        x = x.view(-1, 256 * 3 * 3)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.final_activation(self.fc3(x))
        return x

net = Net()


'''
PART 4:
Choose a good loss function and optimizer
'''

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(net.parameters(), lr=0.001)


'''
PART 5:
Train your model!
'''

num_epochs = 5
losses = []  

for epoch in range(num_epochs):
    print("EPOCH:", epoch)
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        print(len(inputs), len(labels))
        optimizer.zero_grad()
        outputs = net(inputs)
        print(len(outputs), len(labels))
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    epoch_loss = running_loss / len(train_loader)
    print(f"Epoch {epoch+1}, Training loss: {epoch_loss}")
    losses.append(epoch_loss) 



print('Finished Training')


'''
PART 6:
Evalute your model! Accuracy should be greater or equal to 80%

'''

correctImage = None
wrongImage = None
correct = 0
total = 0
with torch.no_grad():
    for data in train_loader:
        images, labels = data
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        if correctImage is None or wrongImage is None:
            for i in range(labels.size(0)):
                if correctImage is None and predicted[i] == labels[i]:
                    correctImage = images[i]
                    correctLabel = labels[i]
                elif wrongImage is None and predicted[i] != labels[i]:
                    wrongImage = images[i]
                    wrongLabel = labels[i]
                if correctImage is not None and wrongImage is not None:
                    break
            
def imshow(img):
    img = img / 2 + 0.5    
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()

print('A correct example:')
imshow(torchvision.utils.make_grid(correctImage))
print('Correct Label:', correctLabel.item())

print('A wrong example:')
imshow(torchvision.utils.make_grid(wrongImage))
print('Predicted Label:', wrongLabel.item())

print('Accuracy: %f %%' % (100 * correct / total))


'''
PART 7:
Check the written portion. You need to generate some plots. 
'''
plt.plot(range(num_epochs), losses, label='Training Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Training Loss Over Time')
plt.legend()
plt.show()
