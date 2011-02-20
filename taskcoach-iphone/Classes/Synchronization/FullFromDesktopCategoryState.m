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
#import "LogUtils.h"

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
	JLDEBUG("=== Full from desktop categories");

	[self startWithFormat:"ssz" count:myController.categoryCount];
}

- (void)onNewObject:(NSArray *)value
{
	CDCategory *category = [NSEntityDescription insertNewObjectForEntityForName:@"CDCategory" inManagedObjectContext:getManagedObjectContext()];

	JLDEBUG("Getting category \"%s\"", [[value objectAtIndex:0] UTF8String]);
	
	JLDEBUG("Category name length: %d", [[value objectAtIndex:0] length]);
	JLDEBUG("Category ID length: %d", [[value objectAtIndex:1] length]);

	category.creationDate = [NSDate date];
	category.file = [Configuration configuration].cdCurrentFile;
	category.name = [value objectAtIndex:0];
	category.taskCoachId = [value objectAtIndex:1];
	category.status = [NSNumber numberWithInt:STATUS_NONE];
	
	if ([value objectAtIndex:2] != [NSNull null])
	{
		JLDEBUG("Category parent ID length: %d", [[value objectAtIndex:2] length]);

		[parentReq setPredicate:[NSPredicate predicateWithFormat:@"taskCoachId == %@", [value objectAtIndex:2]]];
		NSError *error;
		NSArray *results = [getManagedObjectContext() executeFetchRequest:parentReq error:&error];
		if (results)
		{
			JLDEBUG("Category parent count: %d", [results count]);
			category.parent = [results objectAtIndex:0];
		}
		else
		{
			JLERROR("Could not find parent: %s", [[error localizedDescription] UTF8String]);
		}
	}

	JLDEBUG("Got category \"%s\"", [category.name UTF8String]);

	[myController increment];
	[self sendFormat:"i" values:[NSArray arrayWithObject:[NSNumber numberWithInt:1]]];
}

- (void)onFinished
{
	JLDEBUG("=== Finished");

	myController.state = [FullFromDesktopTaskState stateWithNetwork:myNetwork controller:myController];
}

@end
