# What is an API?

- **API (Application Programming Interface)** is a collection of communication protocols and subroutines.  
- It enables **different programs** to communicate with each other.  
- APIs provide **developers** with efficient tools to build software programs.  
- APIs help **two applications** communicate by:  
  - Receiving a request from the user.  
  - Sending the request to the service provider.  
  - Returning the result from the service provider to the user.   

---

# How do APIs Work?

The working of an API can be clearly explained with a few simple steps. Think of a **client-server architecture** where:  

- The **client** sends the request via a medium to the **server** and receives the response through the same medium.  
- The **API** acts as a communication medium between two programs or systems.  
- The **client** is the user/customer (who sends the request), the **medium** is the **Application Programming Interface**, and the **server** is the backend (where the request is processed and a response is provided).  
### Steps followed in the working of APIs:

1. The client initiates the request via the API's **URI** (Uniform Resource Identifier).  
2. The API makes a call to the server after receiving the request.  
3. The server processes the request and sends the response back to the API.  
4. Finally, the API transfers the data to the client.  
-----
# How is an API Different From a Web Application?

An **API** acts as an interface that allows proper communication between two programs, whereas a **web application** is a network-based resource responsible for completing a single task.  

It's important to know that:  
> **"All web services are APIs, but not all APIs are web services."**  

The key difference between an **API** and a **web application** is:  
- **API** allows **two-way communication** between systems.  
- **Web applications** are just a way for users to interact through a web browser.  
- A web application may have an API to complete requests.  

---

# Types of APIs  

There are three basic types of APIs:  

### 1. Web APIs  
A **Web API** (also called **Web Services**) is an extensively used API over the web that can be accessed using **HTTP protocols**.  
- Web APIs are open-source and can be used by a large number of clients through **phones, tablets, or PCs**.  

### 2. Local APIs  
**Local APIs** provide middleware services to programmers.  
- Examples: **TAPI** (Telephony Application Programming Interface) and **.NET APIs**.  

### 3. Program APIs  
**Program APIs** make a remote program appear as if it is running locally by using **Remote Procedural Calls (RPCs)**.  
- Example: **SOAP (Simple Object Access Protocol)**.  

---

# Other Types of APIs  

### 1. SOAP (Simple Object Access Protocol)  
- Defines messages in **XML format**.  
- Used by web applications to communicate with each other.  

### 2. REST (Representational State Transfer)  
- Uses **HTTP methods** like **GET, POST, PUT, DELETE** to transfer data.  
- Designed to take advantage of existing web standards.  

### 3. JSON-RPC  
- Uses **JSON** for data transfer.  
- A lightweight **Remote Procedural Call (RPC)** with a simple data structure.  

### 4. XML-RPC  
- Based on **XML** and uses **HTTP** for data transfer.  
- Commonly used for exchanging information between multiple networks.