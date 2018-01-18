# perception-model-tool

We present a model allowing inferences of perceivable screen content in relation to position and orientation of mobile or wearable devices with respect to their user. The model is based on findings from vision science and allows prediction of a value of effective resolution that can be perceived by a user. It considers distance and angle between the device and the eyes of the observer as well as the resulting retinal eccentricity when the device is not directly focused but observed in the periphery. To validate our model, we conducted a study with 12 participants. Based on our results, we outline implications for the design of mobile applications that are able to adapt themselves to facilitate information throughput and usability.

To visualize the predictions of the model, we provide a tool that – given a display position and orientation in relation to the user’s eyes – renders a picture representing the effective display resolution, e.g. to assess text readability for different sizes or fonts. We distinguish whether a person is (a) directly looking at the display or (b) looking straight ahead and observing the display in the periphery. The tool takes a picture, e.g. a screenshot of a smartwatch application, converts it to the CIE L*a*b* space, and only the luminance information is further considered. A second-order Butterworth filter is used to remove frequencies that would not be visible according to our model.

Please see here for the full paper: https://doi.org/10.1145/3173574.3174184


Example usage
-------------
```
python filter_screenshot.py ./image.png ./out.png -d 0.4 -s 0.02 0.02 -r 200 200 -ha 10 -va 20
```

For a full list of commands see the help page
```
python filter_screenshot.py --help
```
