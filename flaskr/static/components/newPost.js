
function setDate() {
    const selectedDate = document.getElementById('modalDate').value;
    document.getElementById('date').value = selectedDate;
    $('#dateModal').modal('hide');
}

function selectJournal(journal) {
  document.getElementById('journal').value = journal;
  $('#journalModal').modal('hide');
}

function openNewJournalModal() {

  document.getElementById('journalModalLabel').innerText = 'Create New Journal';

  /*
  * This function is used to create a new Journal. 
  * In the future the selecct function should be a search connected to the API
  */
  const modalBody = `
      <div class="form-group">
          <label for="newJournalName">Journal Name</label>
          <input type="text" class="form-control" id="newJournalName" placeholder="Enter journal name" required>
      </div>
      <div class="form-group">
          <label for="journalColor">Choose Plant</label>
          <select class="form-control" id="plantType">
            <option value="">Select a plant type</option>
            <option value="succulent">Succulent</option>
            <option value="fern">Fern</option>
            <option value="flowering">Flowering Plant</option>
            <option value="cactus">Cactus</option>
            <option value="tree">Tree</option>
            <option value="herb">Herb</option>
          </select>
     </div>
  `;


  const journalModalBody = document.querySelector('#journalModal .modal-body');
  journalModalBody.innerHTML = modalBody;

  
  const journalModalFooter = document.querySelector('#journalModal .modal-footer');
  journalModalFooter.innerHTML = `
      <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" onclick="createNewJournal()">Create Journal</button>
  `;

 
  $('#journalModal').modal('show');
}
/*
* This is the logic used to get the new Journal data
* Once back end gets to it it'll be more robust
*/
function createNewJournal() {
  const journalName = document.getElementById('newJournalName').value;

  if (journalName && journalColor) {
      $('#journalModal').modal('hide'); 
  } else {
      alert("Please enter a journal name and select a plant.");
  }
}