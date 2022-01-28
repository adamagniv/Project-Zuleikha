```
@@@@@@@   @@@@@@@    @@@@@@        @@@  @@@@@@@@   @@@@@@@  @@@@@@@            @@@@@@@@  @@@  @@@  @@@       @@@@@@@@  @@@  @@@  @@@  @@@  @@@   @@@@@@ 
@@@@@@@@  @@@@@@@@  @@@@@@@@       @@@  @@@@@@@@  @@@@@@@@  @@@@@@@            @@@@@@@@  @@@  @@@  @@@       @@@@@@@@  @@@  @@@  @@@  @@@  @@@  @@@@@@@@
@@!  @@@  @@!  @@@  @@!  @@@       @@!  @@!       !@@         @@!                   @@!  @@!  @@@  @@!       @@!       @@!  @@!  !@@  @@!  @@@  @@!  @@@
@@!  @@@  @@!  @@@  @@!  @@@       @@!  @@!       !@@         @@!                   @@!  @@!  @@@  @@!       @@!       @@!  @@!  !@@  @@!  @@@  @@!  @@@
@!@@!@!   @!@!!@!   @!@  !@!       !!@  @!!!:!    !@!         @!!                 @!!    @!@  !@!  @!!       @!!!:!    !!@  @!@@!@!   @!@!@!@!  @!@!@!@!
!!@!!!    !!@!@!    !@!  !!!       !!!  !!!!!:    !!!         !!!                !!!     !@!  !!!  !!!       !!!!!:    !!!  !!@!!!    !!!@!!!!  !!!@!!!!
!!:       !!: :!!   !!:  !!!       !!:  !!:       :!!         !!:               !!:      !!:  !!!  !!:       !!:       !!:  !!: :!!   !!:  !!!  !!:  !!!
:!:       :!:  !:!  :!:  !:!  !!:  :!:  :!:       :!:         :!:              :!:       :!:  !:!   :!:      :!:       :!:  :!:  !:!  :!:  !:!  :!:  !:!
 ::       ::   :::  ::::: ::  ::: : ::   :: ::::   ::: :::     ::               :: ::::  ::::: ::   :: ::::   :: ::::   ::   ::  :::  ::   :::  ::   :::
 :         :   : :   : :  :    : :::    : :: ::    :: :: :     :               : :: : :   : :  :   : :: : :  : :: ::   :     :   :::   :   : :   :   : :
```
# Project-Zuleikha
[Bezalel  Academy of Art and Design](https://www.bezalel.ac.il/en), M.Des Indusrtrial Design - Design and Technology track.</br>
*Digital Language Project*</br>
Guided By: *Sarit Youdelevich*

## Installations
1. Make sure you have install Python version >= 3.7.1
2. Run ```setup.bat```.</br>
to be able to run this script installs:
  * scikit-image
  * numpy
  * scipy
  * matplotlib
  * ipython
  * jupyter
  * pandas
  * sympy
  * nose
  * tensorflow
  * opencv-python
  * pillow
  * h5py
  * keras
  * openai
3. If a GPU is available on your computers please install CUDA and cuDNN (I used CUDA-11.5.1 & cuDNN-8.2.4.15)
4. please download [OpenFace](https://github.com/TadasBaltrusaitis/OpenFace)</br>
Make sure it's under the same root folder as this repo.</br>
Please read the installation guide of OpenFace to make sure you install it correctly before running Zuleikha.
5. make sure to copy your key under the ```api_keys``` folder

## Run
first side runs: ```python -m Zuleikha -k <KEY_FILE_NAME> -m -s```</br>
second side runs: ```python -m Zuleikha -k <KEY_FILE_NAME>```
