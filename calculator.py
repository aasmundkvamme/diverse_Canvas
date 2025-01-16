from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

@app.route('/', methods=['GET', 'POST'])
def calculator():
    if 'memory' not in session:
        session['memory'] = 0
    
    result = ''
    if request.method == 'POST':
        try:
            num1 = float(request.form.get('num1', 0))
            num2 = float(request.form.get('num2', 0))
            operation = request.form.get('operation')
            
            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                if num2 != 0:
                    result = num1 / num2
                else:
                    result = 'Error: Division by zero'
            elif operation == 'memory_store':
                session['memory'] = num1
                result = f'Stored {num1} in memory'
            elif operation == 'memory_recall':
                result = session['memory']
            
            if isinstance(result, (int, float)):
                result = round(result, 4)
                
        except ValueError:
            result = 'Error: Invalid input'
    
    return render_template('calculator.html', result=result, memory=session['memory'])

if __name__ == '__main__':
    app.run(debug=True)
