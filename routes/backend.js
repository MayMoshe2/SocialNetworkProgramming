const { log } = require('console')
const fs = require('fs')
const { spawn } = require('child_process')
const { required } = require('nodemon/lib/config')
// const collection = db.collection('users')

{
  /* <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-firestore.js"></script> */
}

// variables
const dataPath = './data/detailsFromUser.json'

// helper methods
const readFile = (callback, returnJson = false, filePath = dataPath, encoding = 'utf8') => {
  fs.readFile(filePath, encoding, (err, data) => {
    if (err) {
      console.log(err)
    }
    if (!data) data = '{}'
    callback(returnJson ? JSON.parse(data) : data)
  })
}

const writeFile = (fileData, callback, filePath = dataPath, encoding = 'utf8') => {
  fs.writeFile(filePath, fileData, encoding, (err) => {
    if (err) {
      console.log(err)
    }
    callback()
  })
}

const firstPython = (req, res) => {
  try {
    var dataToSend
    const python = spawn('python', ['temp.py'])
    // collect data from script
    python.stdout.on('data', function (data) {
      console.log('Pipe data from python script ...')
      dataToSend = data.toString()
    })
    python.on('close', (code) => {
      console.log(`child process close all stdio with code ${code}`)
      // send data to browser
      res.send(dataToSend)
    })
  } catch (error) {
    console.log(error)
    res.status(500)
  }
}

const withrowPy = (req, res) => {
  try {
    //console.log(req)
    const userId = req.params['value']
    console.log(userId)

    // print(userId)
    const python = spawn('python', ['withdrawConnections.py', userId])
    // collect data from script
    python.stdout.on('data', function (data) {
      console.log('Pipe data from python script ...')
    })
    python.on('close', (code) => {
      console.log(`child process close all stdio with code ${code}`)
      // send data to browser
    })
  } catch (error) {
    console.log(error)
    res.status(500)
  }
}

const addCon = (req, res) => {
  try {
    var dataToSend
    const python = spawn('python', ['addConnections.py'])
    // collect data from script
    python.stdout.on('data', function (data) {
      console.log('add Connections from backend ...')
      dataToSend = data.toString()
    })
    python.on('close', (code) => {
      console.log(`'add Connections child process close all stdio with code ${code}`)
      // send data to browser
      res.send(dataToSend)
    })
  } catch (error) {
    console.log(error)
    res.status(500)
  }
}

const updateJson = function (req, res) {
  try {
    readFile((data) => {
      const userId = req.params['id']
      if (data[userId]) {
        delete data[userId]
      }
      data[userId] = req.body
      writeFile(JSON.stringify(data, null, 2), () => {
        res.status(200).send('user Updated')
      })
    }, true)
  } catch (error) {
    console.log(error)
    res.status(500)
  }
}

const addEmployee = (req, res) => {
  //let name = req.data.name
  console.log('addEmploeefrom backend')
  console.log(req.query.name)
  console.log(req.query.username)
  console.log(req.query.password)

  firstName = req.query.name
  linkdinName = req.query.username
  passlink = req.query.password
}

module.exports = {
  updateJson,
  firstPython,
  writeFile,
  readFile,
  addCon,
  addEmployee,
  withrowPy,
}
