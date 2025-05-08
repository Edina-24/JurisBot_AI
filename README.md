# JurisBot_AI


# Legal Information Extraction System

## 1. Activate the Virtual Environment

To activate the virtual environment, follow the steps below:

- **For Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

- **For Windows**:
  ```bash
  venv\Scripts\activate
  ```

## 2. Install Required Dependencies

Install the necessary dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 3. Set up Environment Variables

Create a `.env` file in the root directory and add the following configuration:

```ini
GROQ_API_KEY=your_groq_api_key
PORT=5000
```

Make sure to replace `your_groq_api_key` with your actual Groq API key.

## 4. Add Your PDF Documents

Place your PDF documents in the `data` folder so the model can process and extract legal information.

## 5. Run the Server
Once everything is set up, you can start the application by running the following command:

```bash
python main.py
```
This will start the application and it will be available at http://localhost:5000.
