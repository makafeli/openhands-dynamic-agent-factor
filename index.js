const { exec } = require("child_process");

function runDynamicAgent(command, args = []) {
  return new Promise((resolve, reject) => {
    const fullCommand = `python3 /workspace/openhands-dynamic-agent-factor/openhands_dynamic_agent_factory/core/cli.py ${command} ${args.join(" ")}`;
    exec(fullCommand, (error, stdout, stderr) => {
      if (error) {
        reject(`Error: ${stderr}`);
      } else {
        resolve(stdout);
      }
    });
  });
}

// Example usage
(async () => {
  try {
    const result = await runDynamicAgent("list-keywords");
    console.log(result);
  } catch (error) {
    console.error(error);
  }
})();