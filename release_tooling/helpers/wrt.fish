# TODO: make version non-static
function wrt
  docker run \
    --env AWS_PROFILE="$AWS_PROFILE" \
    --env AWS_SDK_LOAD_CONFIG=1 \
    --volume ~/.aws:/root/.aws \
    --volume (git rev-parse --show-toplevel):/data \
    --interactive --tty --rm \
    wellcome/release_tooling:76 $argv
end
