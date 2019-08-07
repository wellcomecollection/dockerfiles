workflow "Test and deploy" {
  on       = "push"

  resolves = [
    "Push",
  ]
}

action "Build" {
  uses = "actions/docker/cli@master"
  # This will need to be changed to release_tooling everywhere
  args = "build -t wellcome/release-tooling ./release_tooling"
}

action "Master" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Tag" {
  needs = "Build"
  uses  = "actions/docker/cli@master"

  args  = [
    "tag",
    "wellcome/release-tooling",
    "wellcome/release-tooling:$GITHUB_SHA"
  ]
}

action "Login" {
  needs   = "Tag"
  uses    = "actions/docker/login@master"

  secrets = [
    "DOCKER_USERNAME",
    "DOCKER_PASSWORD"
  ]
}

action "Push" {
  needs = "Login"
  uses  = "actions/docker/cli@master"

  args  = [
    "push",
    "wellcome/release-tooling:$GITHUB_SHA"
  ]
}
