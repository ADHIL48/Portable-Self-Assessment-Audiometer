
<h1 align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Raleway&size=38&duration=3000&pause=1000&color=F39C12&center=true&vCenter=true&width=750&lines=🎧+Portable+Self-Assessment+Audiometer;A+Smart+Way+to+Test+Your+Hearing!">
</h1>

<img src="https://cdni.iconscout.com/illustration/premium/thumb/audiologist-audiometry-hearing-test-screening-illustration-download-in-svg-png-gif-file-formats--exam-cochlea-drum-various-themes-set-151-pack-miscellaneous-illustrations-9643726.png?f=webp" alt="Big Smile Emoji" width="250px" align="right">




## 📝 Overview<img src="https://i0.wp.com/audiocardio.com/wp-content/uploads/2020/07/shutterstock_1073978558.png?fit=1600%2C1036&ssl=1" alt="Big Smile Emoji" width="250px" align="right">

This project focuses on developing a **Portable Self-Assessment Audiometer** using **Raspberry Pi**. The device enables individuals to perform hearing tests without requiring an audiologist, making hearing screening accessible, affordable, and convenient.

## ✨ Features

- 🔹 **Uses Raspberry Pi 3 B+** for signal generation and data processing.
- 🔹 **Pure Tone Audiometry** implementation for hearing self-assessment.
- 🔹 **Python-based software** for tone generation and audiogram visualization.
- 🔹 **Automated threshold detection** using the Hughson Westlake method.
- 🔹 **User-friendly interface** developed with Tkinter for ease of use.
- 🔹 **Portable & cost-effective** alternative to traditional audiometers.
- 🔹 **Data storage** in CSV format for future reference.
- 🔹 **Real-time result visualization** with an interactive audiogram chart.
- 🔹 **Remote accessibility** through VNC for medical professionals.

## 🛠️ Hardware Requirements

- 🖥️ **Raspberry Pi 3 B+** (or later versions)
- 🎧 **Headphones** (TDH-49 recommended for accurate testing)
- 🖱️ **USB Mouse** (for patient response input)
- 🔌 **Power Supply** (5V, 2.5A)
- 🌐 **Ethernet Cable or WiFi Adapter** (for remote access)
- 📺 **External Display (Optional)**

## 💾 Software Requirements

- 🖥️ **Operating System**: Raspbian OS (Raspberry Pi OS)
- 💻 **Programming Language**: Python 3
- 📦 **Required Libraries**:
  - 🟦 NumPy
  - 📊 Matplotlib
  - 📑 Pandas
  - 🎵 PyAudio (for sound processing)
  - 🖼️ Tkinter (for GUI development)
  - 🌍 PyVNC (for remote access)


## 📂 Project Files
This Google Drive has all the **source code & report** of the project.
<p align="center">
  <a href="https://drive.google.com/drive/folders/1BzAvnNeO_ckDrbpHNvytAF8wMDfrcYT7?usp=drive_link">
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSpqGi5vvAo4AE8EZln43IGhzSAZ21J50G2sQ&s" alt="Google Drive"width="300" height="130">
  </a>
</p>

**Note:** Large documents are present in the above drive as GitHub only offers a **25MB max per document**.


  
## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```sh
git clone https://github.com/yourusername/Portable-Self-Assessment-Audiometer.git
cd Portable-Self-Assessment-Audiometer
```

### 2️⃣ Install Dependencies

```sh
pip install numpy matplotlib pandas pyaudio
```

### 3️⃣ Run the Audiometer Software

```sh
python audiometer.py
```

## 🔍 How It Works
<img src="https://cdni.iconscout.com/illustration/premium/thumb/audiologist-audiometry-hearing-test-screening-illustration-download-in-svg-png-gif-file-formats--exam-cochlea-drum-various-themes-set-151-pack-miscellaneous-illustrations-9643726.png?f=webp" alt="Big Smile Emoji" width="250px" align="right">

- 🎵 **Tone Generation**: The system generates **pure tones** at different frequencies ranging from **125 Hz to 8 kHz**.
- 🎧 **User Interaction**: The user listens to tones through headphones and responds by clicking the mouse.
- 🔊 **Volume Adjustment**: The program records responses and automatically adjusts the volume using the **modified Hughson Westlake method**.
- 📈 **Audiogram Creation**: An **audiogram** is generated based on the user’s responses.
- 💾 **Data Storage**: Results are stored in **CSV format** with date and time for future reference.
- 📊 **Graphical Analysis**: The software provides a **graphical analysis** of hearing loss stages and allows comparison over time.


  ## 🎯 Applications

- 🏥 **Hearing self-assessment** for individuals.
- 👨‍⚕️ **Preliminary hearing screening** before professional diagnosis.
- 🧓 **Early detection of hearing loss** in elderly individuals.
- 🔗 **Remote monitoring** by audiologists via VNC.
- 🎓 **Educational purposes** for audiology students and researchers.

## 🔮 Future Enhancements

- 📱 **Integration with mobile applications** for better accessibility.
- 🎶 **Support for bone conduction audiometry**.
- 🤖 **Enhanced machine learning-based threshold prediction**.
- ☁️ **Integration with cloud storage for result tracking**.
- 🌎 **Multi-language support for global usability**.

## 📂 Sample Output

### 1. Thonny IDE
<p align="center">
  <img src="https://drive.google.com/uc?id=1xZTTKmZqqsDxfP2oTtMqpN7NHSTbkqUV" alt="Thonny IDE" width="400" height="210">
</p>

### 2. Instruction of the Project
<p align="center">
  <img src="https://drive.google.com/uc?id=1BVywSZr15OhsMOs6yYCfU5ImTBobwGFl" alt="Instruction of the project" width="400" height="210">
</p>

### 2.1 Instruction
<p align="center">
  <img src="https://drive.google.com/uc?id=1oxiwlaW8vG_mO89A93uVELsNSGd2FHUD" alt="Instruction" width="400" height="210">
</p>

### 3. Patient Response Screen
<p align="center">
  <img src="https://drive.google.com/uc?id=12gDjTd6GUO0dmNO5Y8YjLpF-RPkVDf9L" alt="Patient Response Screen" width="400" height="210">
</p>

### 4. Output (Audiogram)
<p align="center">
  <img src="https://drive.google.com/uc?id=110X1iqZQeCamlx_UDtbSiH7NwFf89iN4" alt="Output Audiogram" width="400" height="210">
</p>

### 4.1 Audiogram
<p align="center">
  <img src="https://drive.google.com/uc?id=1BJKeN1-JELR8IS8kKJDI-pT-E02yxNa5" alt="Audiogram" width="400" height="210">
</p>

### 5. Test Analysis
<p align="center">
  <img src="https://drive.google.com/uc?id=1V0ftPbFwy7F9bCu73YRqHvza2t1deVJA" alt="Test Analysis" width="400" height="210">
</p>

### 6. Portable Audiometer
<p align="center">
  <img src="https://drive.google.com/uc?id=1o_JZTUVvtq0rBPNjdmPWrJLBhonzd_gr" alt="Portable Audiometer" width="400" height="210">
</p>







---

## 👨‍💻 Project Contributors

- **Adhil M** (Founder & Maintainer)
- 👤 **Pranesh S**
- 👤 **Naveen S**

---
  ## 📜 License

This project is open-source and available under the **MIT License**.

---
## ⭐ Support This Project
If you found this helpful, **⭐ star this repo!**  
It helps this project become more visible to others and supports future contributions.  
---
Thank you for your support! 🚀  



