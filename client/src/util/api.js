
 function updateTime(setCurrentTimeCallback) {
    fetch('/api/time').then(res => res.json()).then(data => {
        setCurrentTimeCallback(data.time);
    });
}

 function getProjectFunctions(pathToProject) {
     return new Promise((doResolve, doReject) => {
         fetch('/api/get_functions_for_project', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 "pathToProject": pathToProject
             }),
         }).then(res => res.json()).then(data => {
             if (data.status === "OK") {
                 doResolve(data);
             } else {
                 doReject(data);
             }
         });
     });
 }

 function getProjectTest(pathToProject) {
     return new Promise((doResolve, doReject) => {
         fetch('/api/get_tests_for_project', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 "pathToProject": pathToProject
             }),
         }).then(res => res.json()).then(data => {
             if (data.status === "OK") {
                 doResolve(data);
             } else {
                 doReject(data);
             }
         });
     });
 }

 export {updateTime, getProjectFunctions, getProjectTest};
