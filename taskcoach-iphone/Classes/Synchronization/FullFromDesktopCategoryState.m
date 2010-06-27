//
//  FullFromDesktopCategoryState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 06/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "SyncViewController.h"
#import "Configuration.h"
#import "FullFromDesktopCategoryState.h"
#import "FullFromDesktopTaskState.h"
#import "CDCategory.h"
#import "CDDomainObject+Addons.h"

@implementation FullFromDesktopCategoryState

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[FullFromDesktopCategoryState alloc] initWithNetwork:network controller:controller] autorelease];
}

- initWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	if ((self = [super initWithNetwork:network controller:controller]))
	{
		parentReq = [[NSFetchRequest alloc] init];
		[parentReq setEntity:[NSEntityDescription entityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()]];
	}

	return self;
}

- (void)dealloc
{
	[parentReq release];

	[super dealloc];
}

- (void)activated
{
	[self startWithFormat:"ssz" count:myController.categoryCount];
}

- (void)onNewObject:(NSArray *)value
{
	CDCategory *category = [NSEntityDescription insertNewObjectForEntityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()];

	category.creationDate = [NSDate date];
	category.file = [Configuration configuration].cdCurrentFile;
	category.name = [value objectAtIndex:0];
	category.taskCoachId = [value objectAtIndex:1];
	category.status = [NSNumber numberWithInt:STATUS_NONE];

	if ([value objectAtIndex:2] != [NSNull null])
	{
		[parentReq setPredicate:[NSPredicate predicateWithFormat:@"taskCoachId == %@", [value objectAtIndex:2]]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:parentReq error:&error];
		if (results)
		{
			assert([results count] == 1);
			category.parent = [results objectAtIndex:0];
		}
		else
		{
			NSLog(@"Could not find parent: %@", [error localizedDescription]);
		}
	}

	[myController increment];
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
}

- (void)onFinished
{
	myController.state = [FullFromDesktopTaskState stateWithNetwork:myNetwork controller:myController];
}

@end
