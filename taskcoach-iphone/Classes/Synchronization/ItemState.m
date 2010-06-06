//
//  ItemState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/09/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "ItemState.h"
#import "Network.h"
#import "Configuration.h"

@implementation ItemState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		parser = [[ItemParser alloc] init];
	}
	
	return self;
}

- (void)dealloc
{
	[item release];
	[parser release];
	
	[super dealloc];
}

- (void)startWithFormat:(char *)format count:(NSInteger)theCount
{
	count = theCount;
	
	[item release];
	item = nil;

	if (count || (count == NOCOUNT))
	{
		item = [[parser parse:format] retain];
		
		[myNetwork expect:[[item expect] intValue]];
	}
	else
	{
		[self onFinished];
	}
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	[item feed:data];
	
	NSNumber *expect = [item expect];
	if (expect)
	{
		[myNetwork expect:[expect intValue]];
	}
	else
	{
		NSObject *value = [item.value retain];
		[self onNewObject:(NSArray *)value];

		// XXXFIXME: there are many interlaced calls that may occur here...

		--count;
		if (count)
		{
			[item start];
			[myNetwork expect:[[item expect] intValue]];
		}
		else
		{
			NSLog(@"Finished");
			[self onFinished];
		}
	}
}

- (void)sendFormat:(char *)format values:(NSArray *)values
{
	NSMutableData *data = [[NSMutableData alloc] init];
	BaseItem *it = [parser parse:format];
	[it packValue:values inData:data];
	[myNetwork append:data];
	[data release];
}

- (void)onNewObject:(NSArray *)value
{
}

- (void)onFinished
{
}

- (NSNumber *)countForEntityName:(NSString *)entityName status:(NSInteger)status
{
	NSFetchRequest *req = [[NSFetchRequest alloc] init];
	[req setEntity:[NSEntityDescription entityForName:entityName inManagedObjectContext:getManagedObjectContext()]];
	[req setPredicate:[NSPredicate predicateWithFormat:@"file == %@ AND status == %d", [Configuration configuration].cdCurrentFile, status]];
	
	NSError *error;
	NSInteger eCount = [getManagedObjectContext() countForFetchRequest:req error:&error];
	if (eCount < 0)
	{
		NSLog(@"Error counting %@: %@", entityName, [error localizedDescription]);
		eCount = 0;
	}
	[req release];
	
	NSLog(@"Count for status: %d entity: %@ => %d", status, entityName, eCount);
	
	return [NSNumber numberWithInt:eCount];
}

@end
