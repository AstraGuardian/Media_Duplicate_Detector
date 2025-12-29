# Contributing to Media Duplicate Detector

First off, thank you for considering contributing! Every contribution helps make this project better.

## About Contributions

This project is maintained by someone who isn't a professional developer—I built it with Claude Code's help to solve my own problem. **That means your expertise is genuinely valuable here**, whether you're fixing bugs, improving code quality, adding features, or even just reviewing code.

### What I'm Looking For

All contributions are welcome:
- 🐛 **Bug fixes** - If you found it and can fix it, please do!
- ✨ **New features** - Useful additions that fit the project's scope
- 📚 **Documentation** - Improvements, clarifications, screenshots, examples
- 🔍 **Code review** - Suggestions for better practices, security, or performance
- 🧪 **Tests** - We don't have automated tests yet; this would be amazing!
- 🎨 **UI improvements** - Better layouts, themes, icons, usability

### Response Time Expectations

**Please be patient**:
- I review PRs when I have time, usually weekly or bi-weekly
- I use Claude Code to help me understand and evaluate changes
- Complex PRs may take longer as I work through them
- If something is urgent for you, feel free to fork the project

This doesn't mean your contribution isn't valued—it just means I'm managing this alongside everything else in life!

## How to Contribute

### Reporting Bugs

Found a bug? Please [open an issue](https://github.com/AstraGuardian/Media_Duplicate_Detector/issues/new/choose) with:
- What you expected to happen
- What actually happened
- Steps to reproduce the issue
- Your OS and Python version
- Any error messages (if applicable)

### Suggesting Features

Have an idea? [Open an issue](https://github.com/AstraGuardian/Media_Duplicate_Detector/issues/new/choose) to discuss it first:
- Describe the feature and why it's useful
- Explain how it would work from a user's perspective
- Consider if it fits the project's scope (managing duplicate video files)

This helps avoid wasted effort if the feature doesn't align with the project goals.

### Submitting Pull Requests

#### Before You Start

1. **Check existing issues** - Someone might already be working on it
2. **Discuss major changes** - Open an issue first for big features or refactors
3. **Keep it focused** - One PR per feature/fix makes review easier

#### The Process

1. **Fork the repository**
   ```bash
   git clone https://github.com/AstraGuardian/Media_Duplicate_Detector.git
   cd Media_Duplicate_Detector
   ```

2. **Create a branch**
   ```bash
   git checkout -b fix/your-bug-fix
   # or
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style (or improve it!)
   - Add comments where things aren't obvious
   - Test on both Windows and Linux if possible

4. **Commit your changes**
   ```bash
   git commit -m "Fix: brief description of what you fixed"
   # or
   git commit -m "Feature: brief description of new feature"
   ```

5. **Push and create a PR**
   ```bash
   git push origin your-branch-name
   ```
   Then open a pull request on GitHub.

#### PR Guidelines

**Good PRs include**:
- Clear title describing what it does
- Description of the problem and your solution
- Any relevant issue numbers (`Fixes #123`)
- Screenshots for UI changes
- Notes on testing you've done

**Example PR description**:
```
## What This Fixes
Fixes #42 - App crashes when scanning network drives on Linux

## How It Works
Added better error handling in scanner.py to catch permission errors
on mounted shares. Now shows a user-friendly message instead of crashing.

## Testing
Tested on:
- Ubuntu 22.04 with CIFS mount
- Windows 11 with UNC path
```

### Code Style

There's no strict style guide, but please:
- Keep it readable and simple
- Add comments for non-obvious logic
- Use meaningful variable names
- Follow the patterns you see in existing code

If you want to refactor/clean up code, that's welcome! Just explain what and why in your PR.

### Testing

We don't currently have automated tests (contributions welcome!). Please:
- Test your changes manually
- Try both Windows and Linux if you can
- Test edge cases (empty folders, permission errors, network issues, etc.)

## Types of Contributions

### 🐛 Bug Fixes
- Always welcome
- Include reproduction steps in your PR
- Explain what was wrong and how you fixed it

### ✨ Features
- Discuss in an issue first for anything major
- Keep features focused and user-friendly
- Consider how it fits with existing functionality

### 📚 Documentation
- Fix typos, clarify confusing parts
- Add examples or screenshots
- Improve installation or usage instructions
- No need to open an issue first for docs!

### 🎨 UI/UX Improvements
- Better layouts or visual design
- Improved user flows
- Accessibility improvements
- Show before/after screenshots in your PR

### 🔒 Security
- Security issues should be reported privately first
- Open an issue marked as security-related
- I'll work with you to fix it before public disclosure

## What Happens After You Submit

1. **I'll review when I can** - Usually within 1-2 weeks
2. **I'll use Claude Code to help understand** - Especially for complex changes
3. **I might ask questions** - To understand the approach or clarify things
4. **I might request changes** - To align with project goals or improve the solution
5. **I'll merge or explain why not** - With appreciation either way

### If Your PR Isn't Merged

It's not personal! Some reasons PRs might not be merged:
- Doesn't fit the project scope or goals
- Too complex for me to maintain given my skill level
- Needs changes that you don't have time to make
- There's a simpler approach

**But your effort isn't wasted!** You can:
- Fork the project and include it in your version
- Keep the code for future use
- You learned something by contributing

## Code of Conduct

Be kind, respectful, and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Questions?

Not sure about something? Just ask!
- Open an issue with your question
- Discussion is welcome and encouraged

## Thank You!

Seriously, thank you for contributing. Whether it's a one-line typo fix or a major feature, it's appreciated. Open source works because people like you care enough to help improve things.

Happy coding! 🎉
