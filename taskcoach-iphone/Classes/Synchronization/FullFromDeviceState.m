//
//  FullFromDeviceState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "FullFromDeviceState.h"
#import "FullFromDeviceTaskState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"
#import "String+Utils.h"

@implementation FullFromDeviceState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if (self = [super initWithNetwork:network controller:controller])
	{
		categoryIds = [[NSMutableArray alloc] initWithCapacity:32];
	}
	
	return self;
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDeviceState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)dealloc
{
	[categoryIds release];
	
	[super dealloc];
}

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Synchronizing...", @"Synchronizing title");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;

	[[[Database connection] statementWithSQL:@"DELETE FROM Meta WHERE name='guid'"] exec];

	[myNetwork expect:4];

	Statement *req;
	
	req = [[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM Category"];
	[req execWithTarget:self action:@selector(onCategoryCount:)];
	
	req = [[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM Task"];
	[req execWithTarget:self action:@selector(onTaskCount:)];
	
	req = [[Database connection] statementWithSQL:@"SELECT * FROM Category"];
	[req execWithTarget:self action:@selector(onCategory:)];
}

- (void)onCategoryCount:(NSDictionary *)dict
{
	categoryCount = [[dict objectForKey:@"total"] intValue];
	[myNetwork appendInteger:categoryCount];
}

- (void)onTaskCount:(NSDictionary *)dict
{
	total = categoryCount + [[dict objectForKey:@"total"] intValue];
	[myNetwork appendInteger:[[dict objectForKey:@"total"] intValue]];
}

- (void)onCategory:(NSDictionary *)dict
{
	NSLog(@"Pushing category %@", [dict objectForKey:@"name"]);

	[categoryIds addObject:[dict objectForKey:@"id"]];
	[myNetwork appendString:[dict objectForKey:@"name"]];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	switch (state)
	{
		case 0:
			state = 1;
			[network expect:ntohl(*((int32_t *)[data bytes]))];
			break;
		case 1:
		{
			Statement *req = [[Database connection] statementWithSQL:@"UPDATE Category SET taskCoachId=? WHERE id=?"];
			[req bindString:[NSString stringFromUTF8Data:data] atIndex:1];
			[req bindInteger:[[categoryIds objectAtIndex:0] intValue] atIndex:2];
			[req exec];
			[categoryIds removeObjectAtIndex:0];

			categoryCount -= 1;
			count += 1;
			myController.progress.progress = 1.0 * count / total;
			
			if (categoryCount)
			{
				state = 0;
				[network expect:4];
			}
			else
			{
				controller.state = [FullFromDeviceTaskState stateWithNetwork:network controller:controller];
			}

			break;
		}
	}
}

@end
