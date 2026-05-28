#import <React/RCTBridgeModule.h>
#import <React/RCTEventEmitter.h>

/// Objective-C bridge header required by React Native to expose the Swift module.
@interface RCT_EXTERN_MODULE(ScreenCaptureModule, RCTEventEmitter)

RCT_EXTERN_METHOD(
  startCapture:(NSString *)host
  port:(nonnull NSNumber *)port
  resolver:(RCTPromiseResolveBlock)resolve
  rejecter:(RCTPromiseRejectBlock)reject
)

RCT_EXTERN_METHOD(
  stopCapture:(RCTPromiseResolveBlock)resolve
  rejecter:(RCTPromiseRejectBlock)reject
)

@end
