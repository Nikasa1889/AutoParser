/* initialise variables */

var inputTitle = document.querySelector('.new-note input');
var inputBody = document.querySelector('.new-note textarea');

var noteContainer = document.querySelector('.note-container');


var clearBtn = document.querySelector('.clear');
var addBtn = document.querySelector('.add');

/*  add event listeners to buttons */

addBtn.addEventListener('click', addNote);
clearBtn.addEventListener('click', clearAll);

/* display previously-saved stored notes on startup */

initialize();

function initialize() {
  chrome.storage.local.get(null,function(results) {
    if(chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError);
    } else {
      var noteKeys = Object.keys(results);
      for(i = 0; i < noteKeys.length; i++) {
        var curKey = noteKeys[i];
        var curValue = results[curKey];
        displayNote(curKey,curValue);
      }
    }
  });
}

/* Add a note to the display, and storage */

function addNote() {
  var noteTitle = inputTitle.value;
  var noteBody = inputBody.value;
  chrome.storage.local.get(noteTitle, function(result) {
    var objTest = Object.keys(result);
    if(objTest.length < 1 && noteTitle !== '' && noteBody !== '') {
      inputTitle.value = '';
      inputBody.value = '';
      storeNote(noteTitle,noteBody);
    }
  })
}

/* function to store a new note in storage */

function storeNote(title, body) {
  chrome.storage.local.set({ [title] : body }, function() {
    if(chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError);
    } else {
      displayNote(title,body);
    }
  });
}

/* function to display a note in the note box */

function displayNote(title, body) {

  /* create note display box */
  var note = document.createElement('div');
  var noteDisplay = document.createElement('div');
  var noteH = document.createElement('h2');
  var notePara = document.createElement('p');
  var deleteBtn = document.createElement('button');
  var clearFix = document.createElement('div');

  note.setAttribute('class','note');

  noteH.textContent = title;
  notePara.textContent = body.substring(0, 200);
  deleteBtn.setAttribute('class','delete');
  deleteBtn.textContent = 'Delete note';
  clearFix.setAttribute('class','clearfix');

  noteDisplay.appendChild(noteH);
  noteDisplay.appendChild(notePara);
  noteDisplay.appendChild(deleteBtn);
  noteDisplay.appendChild(clearFix);

  note.appendChild(noteDisplay);

  /* set up listener for the delete functionality */

  deleteBtn.addEventListener('click',function(e){
    evtTgt = e.target;
    evtTgt.parentNode.parentNode.parentNode.removeChild(evtTgt.parentNode.parentNode);
    chrome.storage.local.remove(title);
  })

  /* create note edit box */
  var noteEdit = document.createElement('div');
  var noteTitleEdit = document.createElement('input');
  var noteBodyEdit = document.createElement('textarea');
  var clearFix2 = document.createElement('div');

  var updateBtn = document.createElement('button');
  var cancelBtn = document.createElement('button');

  updateBtn.setAttribute('class','update');
  updateBtn.textContent = 'Update note';
  cancelBtn.setAttribute('class','cancel');
  cancelBtn.textContent = 'Cancel update';

  noteEdit.appendChild(noteTitleEdit);
  noteTitleEdit.value = title;
  noteEdit.appendChild(noteBodyEdit);
  noteBodyEdit.textContent = body;
  noteEdit.appendChild(updateBtn);
  noteEdit.appendChild(cancelBtn);

  noteEdit.appendChild(clearFix2);
  clearFix2.setAttribute('class','clearfix');

  note.appendChild(noteEdit);

  noteContainer.appendChild(note);
  noteEdit.style.display = 'none';

  /* set up listeners for the update functionality */

  noteH.addEventListener('click',function(){
    noteDisplay.style.display = 'none';
    noteEdit.style.display = 'block';
  })

  notePara.addEventListener('click',function(){
    noteDisplay.style.display = 'none';
    noteEdit.style.display = 'block';
  }) 

  cancelBtn.addEventListener('click',function(){
    noteDisplay.style.display = 'block';
    noteEdit.style.display = 'none';
    noteTitleEdit.value = title;
    noteBodyEdit.value = body;
  })

  updateBtn.addEventListener('click',function(){
    if(noteTitleEdit.value !== title || noteBodyEdit.value !== body) {
      updateNote(title,noteTitleEdit.value,noteBodyEdit.value);
      note.parentNode.removeChild(note);
    } 
  });
}


/* function to update notes */

function updateNote(delNote,newTitle,newBody) {
  chrome.storage.local.set({ [newTitle] : newBody }, function() {
    if(delNote !== newTitle) {
      chrome.storage.local.remove(delNote, function() {
        displayNote(newTitle, newBody);
      });
    } else {
      displayNote(newTitle, newBody);
    }
  });
}

/* Clear all notes from the display/storage */

function clearAll() {
  while (noteContainer.firstChild) {
      noteContainer.removeChild(noteContainer.firstChild);
  }
  chrome.storage.local.clear();
}