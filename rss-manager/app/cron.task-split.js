const fs = require("fs");
const path = require("path");
const { processTask } = require("./taskProcessor");

async function do_action() {
    let tasks = fs.existsSync(path.join(__dirname, "data", "tasks.json")) && JSON.parse(fs.readFileSync(path.join(__dirname, "data", "tasks.json"))) || [];

    let tasksUpdated = false;

    for (const index in tasks) {
        const task = tasks[index];

        const result = await processTask(task, false);

        if (result && result.success) {
            tasks[index] = task;
            tasksUpdated = true;
        }
    }

    if (tasksUpdated) {
        fs.writeFileSync(path.join(__dirname, "data", "tasks.json"), JSON.stringify(tasks));
    }
}

do_action();
