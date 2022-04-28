
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

 function getFunction(pathToProject, fileId) {
    return new Promise((doResolve, doReject) => {
        fetch('/api/read_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "pathToProject": pathToProject,
                "fileId":fileId,
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

 function saveTest(pathToProject, fileId, functionId, testModule) {
     return new Promise((doResolve, doReject) => {
         fetch('/api/save_test', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 "pathToProject": pathToProject,
                 "fileId": fileId,
                 "functionId": functionId,
                 "testModule": testModule
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

 function updateTest(testId, testModule, customName) {
     return new Promise((doResolve, doReject) => {
         fetch('/api/edit_test', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 "testId": testId,
                 "testModule": testModule,
                 "customName": customName,
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

 function deleteTest(testId) {
     return new Promise((doResolve, doReject) => {
         fetch('/api/delete_test', {
             method: 'POST',
             headers: {
                 'Content-Type': 'application/json',
             },
             body: JSON.stringify({
                 "testId": testId,
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

 export {updateTime, getProjectFunctions, getProjectTest, getFunction, saveTest, updateTest, deleteTest};
