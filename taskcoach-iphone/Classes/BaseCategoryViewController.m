//
//  BaseCategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "BaseCategoryViewController.h"
#import "Category.h"
#import "Database.h"
#import "Statement.h"


@implementation BaseCategoryViewController

- (void)addCategory:(NSDictionary *)dict
{
	Category *category = [[Category alloc] initWithId:[[dict objectForKey:@"id"] intValue] name:[dict objectForKey:@"name"]
											   status:[[dict objectForKey:@"status"] intValue] taskCoachId:[dict objectForKey:@"taskCoachId"]
											 parentId:[dict objectForKey:@"parentTaskCoachId"]];
	[categories addObject:category];
}

- (void)loadCategories
{
	[categories removeAllObjects];
	
	// We're assuming that there are not a bunch of categories, therefore we keep them in memory.
	// This is not the case with tasks.
	
	Statement *req = [[Database connection] statementWithSQL:@"SELECT * FROM Category WHERE status != 3 ORDER BY name"];
	[req execWithTarget:self action:@selector(addCategory:)];
	
	NSMutableDictionary *dict = [[NSMutableDictionary alloc] initWithCapacity:8];
	NSMutableArray *rootItems = [[NSMutableArray alloc] initWithCapacity:8];
	
	for (Category *category in categories)
	{
		if (category.taskCoachId)
		{
			[dict setObject:category forKey:category.taskCoachId];
			if (!category.parentId)
				[rootItems addObject:category];
		}
		else
		{
			[rootItems addObject:category];
		}
	}
	
	for (Category *category in categories)
	{
		if (category.parentId)
		{
			Category *parent = [dict objectForKey:category.parentId];
			[parent addChild:category];
		}
	}
	
	[categories removeAllObjects];
	for (Category *category in rootItems)
	{
		[category finalizeChildren:categories];
	}
	
	[dict release];
	[rootItems release];
}


- (void)viewDidLoad
{
	categories = [[NSMutableArray alloc] init];
	[self loadCategories];
	
	[super viewDidLoad];
}

- (void)viewDidUnload
{
	[categories release];
	categories = nil;
	
	// XXXFIXME: compiler warning here. WTF ?
    //[super viewDidUnload];
}

- (void)fillCell:(UITableViewCell *)cell forCategory:(Category *)category
{
#ifdef __IPHONE_3_0
	cell.textLabel.text = category.name;
#else
	cell.text = category.name;
#endif
	cell.indentationLevel = category.level;
}

#pragma mark Table view methods

- (NSInteger)numberOfSectionsInTableView:(UITableView *)tableView
{
    return 1;
}

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
    return [categories count];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
    static NSString *CellIdentifier = @"Cell";
	
    UITableViewCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil)
	{
        cell = [[[UITableViewCell alloc] initWithFrame:CGRectZero reuseIdentifier:CellIdentifier] autorelease];
    }

	Category *category = [categories objectAtIndex:indexPath.row];
	[self fillCell:cell forCategory:category];
	
    return cell;
}

@end

