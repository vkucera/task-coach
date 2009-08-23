//
//  FullFromDeviceState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 29/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "FullFromDeviceState.h"
#import "FullFromDeviceTaskState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "Database.h"
#import "Statement.h"

@implementation FullFromDeviceState

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller nextState:(NSObject <State> *)next expectIds:(BOOL)expectIds;
{
	if (self = [super initWithNetwork:network controller:controller nextState:next expectIds:expectIds])
	{
		protocolVersion = controller.protocolVersion;
	}
	
	return self;
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDeviceState alloc] initWithNetwork:network controller:controller nextState:[FullFromDeviceTaskState stateWithNetwork:network controller:controller] expectIds:YES] autorelease];
}

- (void)activated
{
	[[[Database connection] statementWithSQL:@"DELETE FROM Meta WHERE name='guid'"] exec];
	
	myController.label.text = NSLocalizedString(@"Synchronizing...", @"Synchronizing title");
	[myController.activity stopAnimating];
	myController.progress.hidden = NO;
	
	[super activated];

	[myNetwork appendInteger:categoryCount];
	[myNetwork appendInteger:taskCount];
	

	// This assumes the primary key is always growing, in order to get parent categories before actual categories
	[self start:[[Database connection] statementWithSQL:[NSString stringWithFormat:@"SELECT * FROM Category WHERE %@ ORDER BY id", [self categoryWhereClause]]]];
}

- (NSString *)tableName
{
	return @"Category";
}

- (void)onParentCategory:(NSDictionary *)dict
{
	NSLog(@"%@", [dict objectForKey:@"taskCoachId"]);

	[myNetwork appendString:[dict objectForKey:@"taskCoachId"]];
}

- (void)onObject:(NSDictionary *)dict
{
	[super onObject:dict];

	[myNetwork appendString:[dict objectForKey:@"name"]];
	
	if (protocolVersion >= 3)
	{
		if ([dict valueForKey:@"parentId"])
		{
			NSLog(@"TCID for %d", [(NSNumber *)[dict valueForKey:@"parentId"] intValue]);

			Statement *req = [[Database connection] statementWithSQL:@"SELECT taskCoachId FROM Category WHERE id=?"];
			[req bindInteger:[(NSNumber *)[dict valueForKey:@"parentId"] intValue] atIndex:1];
			[req execWithTarget:self action:@selector(onParentCategory:)];
		}
		else
		{
			[myNetwork appendInteger:0];
		}
	}
}

@end
