//
//  Network.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Network.h"

@interface Buffer : NSObject
{
	NSData *data;
	NSInteger offset;
}

@property (nonatomic, retain) NSData *data;
@property (nonatomic) NSInteger offset;

- initWithData:(NSData *)data;

@end

@implementation Network

- initWithAddress:(NSString *)address port:(NSInteger)port delegate:(id <NetworkDelegate>)theDelegate
{
	if (self = [super init])
	{
		delegate = theDelegate;
		
		CFReadStreamRef iStream;
		CFWriteStreamRef oStream;
		CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)address, port, &iStream, &oStream);
		
		if (!iStream || !oStream)
		{
			[self dealloc];
			return nil;
		}
		
		inputStream = (NSInputStream *)iStream;
		outputStream = (NSOutputStream *)oStream;
		
		[inputStream retain];
		[outputStream retain];
		
		[inputStream setDelegate:self];
		[outputStream setDelegate:self];
		
		[inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
		[outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];

		[inputStream open];
		[outputStream open];
		
		data = [[NSMutableData data] retain];
		toSend = [[NSMutableArray alloc] init];
	}
	
	return self;
}

- (void)dealloc
{
	[inputStream close];
	[inputStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
	[outputStream close];
	[outputStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];

	[inputStream release];
	[outputStream release];
	[data release];
	[toSend release];
	
	[super dealloc];
}

- (void)expect:(NSInteger)bytes
{
	expecting = bytes;
}

- (void)writeToStream:(NSStream *)stream
{
	Buffer *bf = [toSend objectAtIndex:0];
	unsigned int len = 0;
	
	len = [(NSOutputStream *)stream write:(uint8_t *)[bf.data bytes] + bf.offset maxLength:[bf.data length] - bf.offset];
	bf.offset += len;
	if (bf.offset == [bf.data length])
	{
		[toSend removeObjectAtIndex:0];
	}
}	

- (void)append:(NSData *)theData
{
	Buffer *bf = [[Buffer alloc] initWithData:theData];
	[toSend addObject:bf];
	[bf release];
	
	if (!writing)
		[self writeToStream:outputStream];
}

- (void)stream:(NSStream *)stream handleEvent:(NSStreamEvent)eventCode
{
	switch (eventCode)
	{
		case NSStreamEventOpenCompleted:
			[delegate networkDidConnect:self];
			break;
		case NSStreamEventEndEncountered:
			[delegate networkDidClose:self];
			break;
		case NSStreamEventErrorOccurred:
			[delegate networkDidEncounterError:self];
			break;
		case NSStreamEventHasBytesAvailable:
		{
			uint8_t buffer[1024];
			unsigned int len = 0;
			NSInteger offset = 0;

			len = [(NSInputStream *)stream read:buffer maxLength:1024];
			
			if (len)
			{
				while ([data length] + len - offset >= expecting)
				{
					NSInteger remain = expecting - [data length];
					[data appendBytes:buffer + offset + [data length] length:expecting - [data length]];
					offset += remain;
					
					[delegate network:self didGetData:data];
					[data setLength:0];
				}
				
				if (offset != len)
				{
					[data appendBytes:buffer + offset length:len - offset];
				}
			}

			break;
		}
		case NSStreamEventHasSpaceAvailable:
		{
			if ([toSend count])
			{
				writing = YES;
				[self writeToStream:stream];
			}
			else
			{
				writing = NO;
			}

			break;
		}
	}
}

@end

@implementation Buffer

@synthesize data;
@synthesize offset;

- initWithData:(NSData *)theData
{
	if (self = [super init])
	{
		data = [theData retain];
	}
	
	return self;
}

- (void)dealloc
{
	[data release];
	
	[super dealloc];
}

@end
