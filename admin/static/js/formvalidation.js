function validateAddAnExam(){
    //Ensuring exam end time is after exam start time
    startTime = document.forms["AddAnExam"]["startTime"].value;
    endTime = document.forms["AddAnExam"]["endTime"].value;

    if (startTime > endTime){
        alert("End Time must be later than Start time")
        return false
    }

    //create date format for Duration checking        
    var timeStart = new Date("01/01/2007 " + startTime).getHours();
    var timeEnd = new Date("01/01/2007 " + endTime).getHours();
    var hourDiff = timeEnd - timeStart;  
    Duration = document.forms["AddAnExam"]["Duration"].value;

    if (Duration != hourDiff){
        alert("Wrong duration has been input.")
        return false
    }

    //Ensuring maximum and minimum dates
    examDate = document.forms["AddAnExam"]["date"].value;
    year = examDate.substring(0, 4);

    if (year < '2000'){
         alert("Date cannot be before 2000.")
         return false
    }
    else {
      if (year > '2025'){
          alert("Date cannot be after 2025.")
          return false
        }
     }

}

function checkingNamelist(){
    //Ensuring previous student namelist is deleted before uploading a new one  
    nameoffile = String(document.getElementById("studentNamelistName").value);
    
    if (nameoffile == ''){
         
    }
    else{
    alert('You already have uploaded a student namelist. Please delete before uploading a new one.')
    window.history.back();
    }

}

function uploadingExamPaperName(nameofpaper){
    alert(nameofpaper)
}

function validateEditAnExam(){

    //Ensuring exam end time is after exam start time

    startTime = document.forms["EditAnExam"]["startTime"].value;

    endTime = document.forms["EditAnExam"]["endTime"].value;



    if (startTime > endTime){

        alert("End Time must be later than Start time")

        return false

    }




    //Ensuring maximum and minimum dates

    examDate = document.forms["EditAnExam"]["date"].value;

    year = examDate.substring(0, 4);



    if (year < '2000'){

         alert("Date cannot be before 2000.")

         return false

    }

    else {

      if (year > '2025'){

          alert("Date cannot be after 2025.")

          return false

        }

     }



}
