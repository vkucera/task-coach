//
//  TwoWayState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 01/02/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "TwoWayState.h"
#import "TwoWayNewCategoriesState.h"
#import "Database.h"
#import "Statement.h"
#import "Network.h"
#import "SyncViewController.h"
#import "DomainObject.h"
#import "Configuration.h"

@implementation TwoWayState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[TwoWayState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (NSNumber *)countForEntityName:(NSString *)entityName status:(NSInteger)status
{
	NSNumber *result = [super countForEntityName:entityName status:status];
	totalCount += [result intValue];
	return result;
}

- (void)activated
{
	[self sendFormat:"iiiiiiiii"
			  values:[NSArray arrayWithObjects:
					  [self countForEntityName:@"CDCategory" status:STATUS_NEW],
					  [self countForEntityName:@"CDTask" status:STATUS_NEW],
					  [self countForEntityName:@"CDTask" status:STATUS_DELETED],
					  [self countForEntityName:@"CDTask" status:STATUS_MODIFIED],
					  [self countForEntityName:@"CDCategory" status:STATUS_DELETED],
					  [self countForEntityName:@"CDCategory" status:STATUS_MODIFIED],
					  [self countForEntityName:@"CDEffort" status:STATUS_NEW],
					  [self countForEntityName:@"CDEffort" status:STATUS_MODIFIED],
					  [self countForEntityName:@"CDEffort" status:STATUS_DELETED],
					  nil]];
	
	myController.state = [TwoWayNewCategoriesState stateWithNetwork:myNetwork controller:myController];
}

- (void)onFinished
{
}

@end
