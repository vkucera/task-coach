//
//  Network.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <Foundation/Foundation.h>

@class Network;

@protocol NetworkDelegate

- (void)networkDidConnect:(Network *)network;
- (void)networkDidClose:(Network *)network;
- (void)networkDidEncounterError:(Network *)network;

// This works like asynchat but only with numerical terminators
- (void)network:(Network *)network didGetData:(NSData *)data;

@end

@interface Network : NSObject
{
	NSInputStream *inputStream;
	NSOutputStream *outputStream;
	
	id <NetworkDelegate> delegate;
	NSInteger expecting;
	NSMutableData *data;
	NSMutableArray *toSend;
	BOOL writing;
}

// The delegate is NOT retained
- initWithAddress:(NSString *)address port:(NSInteger)port delegate:(id <NetworkDelegate>)delegate;

- (void)expect:(NSInteger)bytes;
- (void)append:(NSData *)data;

@end
