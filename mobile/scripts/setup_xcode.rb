#!/usr/bin/env ruby
# frozen_string_literal: true

# setup_xcode.rb
#
# Adds the ScreenCapture native module files to the ShareToMac Xcode target.
# Run this once after cloning or after adding new files to ios/ScreenCapture/.
#
# Usage:
#   bundle exec ruby scripts/setup_xcode.rb
#   — or —
#   gem install xcodeproj && ruby scripts/setup_xcode.rb

require "xcodeproj"
require "pathname"

SCRIPT_DIR    = Pathname.new(__FILE__).dirname
IOS_DIR       = (SCRIPT_DIR / "../ios").cleanpath
PROJECT_PATH  = IOS_DIR / "ShareToMac.xcodeproj"
SOURCE_DIR    = IOS_DIR / "ScreenCapture"
TARGET_NAME   = "ShareToMac"
GROUP_NAME    = "ScreenCapture"

# Files to add to the Xcode target
SOURCE_FILES = %w[
  UDPSender.swift
  ScreenCaptureManager.swift
  ScreenCaptureModule.swift
  ScreenCaptureModule.m
].freeze

def main
  abort "Xcode project not found at #{PROJECT_PATH}" unless PROJECT_PATH.exist?
  abort "ScreenCapture source dir not found at #{SOURCE_DIR}" unless SOURCE_DIR.exist?

  project = Xcodeproj::Project.open(PROJECT_PATH)
  target  = project.targets.find { |t| t.name == TARGET_NAME }
  abort "Target '#{TARGET_NAME}' not found in project" unless target

  group = find_or_create_group(project, GROUP_NAME)
  sources_phase = target.source_build_phase

  added = 0
  SOURCE_FILES.each do |filename|
    file_path = SOURCE_DIR / filename
    unless file_path.exist?
      warn "  [skip] #{filename} — file not found"
      next
    end

    # Skip if already referenced in the group
    already_in_group = group.files.any? { |f| f.display_name == filename }
    if already_in_group
      puts "  [ok]   #{filename} already in project"
      next
    end

    # Add file reference to the group.
    # Pass only the filename — the group's sourceTree already anchors it
    # to ios/ScreenCapture/, so using the full relative path would produce
    # a double ScreenCapture/ScreenCapture/ prefix in the build system.
    file_ref = group.new_file(filename)

    # Add to Sources build phase (only .swift and .m files are compiled)
    if filename.end_with?(".swift", ".m")
      sources_phase.add_file_reference(file_ref)
    end

    puts "  [add]  #{filename}"
    added += 1
  end

  # Ensure ReplayKit is linked
  ensure_framework(project, target, "ReplayKit.framework")

  project.save
  puts "\nDone — #{added} file(s) added, project saved."
end

# Returns the group named GROUP_NAME under the main app group,
# creating it if it does not exist.
def find_or_create_group(project, group_name)
  app_group = project.main_group.groups.find { |g| g.display_name == TARGET_NAME }
  abort "Main app group '#{TARGET_NAME}' not found" unless app_group

  existing = app_group.groups.find { |g| g.display_name == group_name }
  return existing if existing

  puts "  [new]  Creating group '#{group_name}'"
  app_group.new_group(group_name, "ScreenCapture")
end

# Links a system framework if it is not already present in the target.
def ensure_framework(project, target, framework_name)
  already_linked = target.frameworks_build_phase.files.any? do |f|
    f.display_name == framework_name
  end

  if already_linked
    puts "  [ok]   #{framework_name} already linked"
    return
  end

  framework_ref = project.frameworks_group.new_file(
    "System/Library/Frameworks/#{framework_name}"
  )
  framework_ref.last_known_file_type = "wrapper.framework"
  framework_ref.source_tree = "SDKROOT"

  target.frameworks_build_phase.add_file_reference(framework_ref)
  puts "  [add]  Linked #{framework_name}"
end

main
