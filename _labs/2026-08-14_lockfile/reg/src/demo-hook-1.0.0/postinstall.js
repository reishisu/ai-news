const fs=require("fs");
fs.writeFileSync(process.env.PWNED_MARKER||"/tmp/pwned.txt","postinstall ran\n");
console.log("demo-hook postinstall executed");
