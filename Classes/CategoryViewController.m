//
//  CategoryViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "NavigationController.h"
#import "CategoryViewController.h"
#import "StringChoiceController.h"
#import "TaskViewController.h"
#import "SyncViewController.h"
#import "FileChooser.h"
#import "BadgedCell.h"
#import "CellFactory.h"

#import "Database/Database.h"
#import "Database/Statement.h"

#import "Domain/Category.h"

#import "Configuration.h"
#import "i18n.h"

@implementation CategoryViewController

@synthesize navigationController;
@synthesize syncButton;
@synthesize fileButton;

- (void)loadCategories
{
	[super loadCategories];
	
	[self editButtonItem].enabled = ([categories count] != 0);
}

- (void)willTerminate
{
	[[PositionStore instance] push:self indexPath:nil type:0];
}

- (void)restorePosition:(Position *)pos store:(PositionStore *)store
{
	[self.tableView setContentOffset:pos.scrollPosition animated:NO];
	
	if (pos.indexPath)
	{
		[self.tableView selectRowAtIndexPath:pos.indexPath animated:NO scrollPosition:UITableViewScrollPositionNone];
		
		TaskViewController *ctrl;
		
		if (pos.indexPath.row)
		{
			ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:pos.indexPath.row - 1] name] category:[[categories objectAtIndex:pos.indexPath.row - 1] objectId] categoryController:self parentTask:nil edit:NO];
		}
		else
		{
			ctrl = [[TaskViewController alloc] initWithTitle:_("All") category:-1 categoryController:self parentTask:nil edit:NO];
		}
		
		[[PositionStore instance] push:self indexPath:pos.indexPath type:pos.type];
		
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
		
		[store restore:ctrl];
	}
}

- (void)viewDidLoad
{
	[super viewDidLoad];
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store.v2"];
	
	if ([fileManager fileExistsAtPath:path])
	{
		PositionStore *store = [[PositionStore alloc] initWithFile:[cachesDir stringByAppendingPathComponent:@"positions.store.v2"]];
		[store restore:self];
		[store release];
	}
	
	[fileManager release];

	fileButton.enabled = ([Database connection].fileNumber >= 2);
}

- (void)viewDidUnload
{
	self.navigationController = nil;
	self.syncButton = nil;
}
- (void)dealloc
{
	[self viewDidUnload];
	
	[super dealloc];
}

- (void)childWasPopped
{
	NSIndexPath *indexPath = [self.tableView indexPathForSelectedRow];

	[[PositionStore instance] pop];

	for (Category *category in categories)
		[category invalidateCache];

	if (indexPath)
	{
		[self.tableView reloadData];

		// XXXFIXME: reloadData is not enough to refresh the task count ?

		for (NSIndexPath *path in [self.tableView indexPathsForVisibleRows])
			[self.tableView deselectRowAtIndexPath:path animated:YES];

		// And the above code does not actually deselect the selected cell. Duh...
		[self.tableView deselectRowAtIndexPath:indexPath animated:YES];
	}
	
	if (wantSync)
	{
		wantSync = NO;
		[self onSynchronize:syncButton];
	}
}

- (void)setWantSync
{
	wantSync = YES;
}

- (IBAction)onChooseFile:(UIBarButtonItem *)button
{
	FileChooser *chooser = [[FileChooser alloc] initWithController:self];
	[self.navigationController presentModalViewController:chooser animated:YES];
	[chooser release];
}

- (IBAction)onAddCategory:(UIBarButtonItem *)button
{
	currentCategory = -1;
	StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onCategoryAdded:(NSString *)name
{
	if (name != nil)
	{
		Statement *req;
		
		if (currentCategory >= 0)
		{
			Category *parent = [categories objectAtIndex:currentCategory];

			req = [[Database connection] statementWithSQL:@"INSERT INTO Category (name, fileId, parentId) VALUES (?, ?, ?)"];
			[req bindInteger:parent.objectId atIndex:3];
		}
		else
			req = [[Database connection] statementWithSQL:@"INSERT INTO Category (name, fileId) VALUES (?, ?)"];

		[req bindString:name atIndex:1];

		if ([Database connection].currentFile)
			[req bindInteger:[[Database connection].currentFile intValue] atIndex:2];
		else
			[req bindNullAtIndex:2];

		[req exec];
		[self loadCategories];
		[self.tableView reloadData];
	}

	[self.navigationController dismissModalViewControllerAnimated:YES];
	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];
}

- (void)fillCell:(BadgedCell *)cell forCategory:(Category *)category
{
	[super fillCell:cell forCategory:category];

	cell.textLabel.text = [category name];
	cell.badge.text = [NSString stringWithFormat:@"%d", [category countForTable:@"AllTask"]];
	cell.badge.capsuleColor = [UIColor blackColor];

	NSInteger count;
	
	count = [category countForTable:@"NotStartedTask"];
	if (count)
	{
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", count] capsuleColor:[UIColor grayColor]];
	}
	
	count = [category countForTable:@"StartedTask"];
	if (count)
	{
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", count] capsuleColor:[UIColor blueColor]];
	}
	
	count = [category countForTable:@"DueSoonTask"];
	if (count)
	{
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", count] capsuleColor:[UIColor orangeColor]];
	}
	
	count = [category countForTable:@"OverdueTask"];
	if (count)
	{
		[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", count] capsuleColor:[UIColor redColor]];
	}
}

- (void)setEditing:(BOOL)editing animated:(BOOL)animated
{
	syncButton.enabled = !editing;

	[self.tableView beginUpdates];
	
	[super setEditing:editing animated:animated];

	NSMutableArray *indexPaths = [[NSMutableArray alloc] initWithCapacity:[categories count]];
	
	if (editing)
	{
		[self.tableView deleteRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationRight];

		for (NSInteger i = 0; i <= [categories count] - 1; ++i)
		{
			[indexPaths addObject:[NSIndexPath indexPathForRow:2*i+1 inSection:0]];
		}
	
		[self.tableView insertRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationRight];
	}
	else
	{
		for (NSInteger i = [categories count] - 1; i >= 0; --i)
		{
			[indexPaths addObject:[NSIndexPath indexPathForRow:i*2+1 inSection:0]];
		}
		
		[self.tableView deleteRowsAtIndexPaths:indexPaths withRowAnimation:UITableViewRowAnimationRight];
		[self.tableView insertRowsAtIndexPaths:[NSArray arrayWithObject:[NSIndexPath indexPathForRow:0 inSection:0]] withRowAnimation:UITableViewRowAnimationRight];
	}
	
	[indexPaths release];

	[self.tableView endUpdates];
}

- (void)deleteCategory:(Category *)category
{
	[category removeAllTasks];

	for (NSInteger i = 0; i < [categories count]; ++i)
	{
		Category *other = [categories objectAtIndex:i];
		
		if ([other.parentId intValue] == category.objectId)
			[self deleteCategory:other];
	}

	if (category.status == STATUS_NEW)
	{
		[category delete];
	}
	else
	{
		[category setStatus:STATUS_DELETED];
	}

	[category save];
}

- (void)tableView:(UITableView *)tableView commitEditingStyle:(UITableViewCellEditingStyle)editingStyle forRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (editingStyle == UITableViewCellEditingStyleDelete)
	{
		[self deleteCategory:[categories objectAtIndex:indexPath.row / 2]];
		[self loadCategories];
		[self.tableView reloadData];
		
		if ([categories count] == 0)
			[self setEditing:NO animated:YES];
	}
	else
	{
		currentCategory = indexPath.row / 2;

		StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
		[self.navigationController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
}

#pragma mark Table view methods

- (NSInteger)tableView:(UITableView *)tableView numberOfRowsInSection:(NSInteger)section
{
	if (self.editing)
	{
		return [super tableView:tableView numberOfRowsInSection:section] * 2;
	}
	else
	{
		return [super tableView:tableView numberOfRowsInSection:section] + 1;
	}
}

- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath
{
	if (self.editing)
	{
		if (indexPath.row % 2)
		{
			currentCategory = indexPath.row / 2;
			
			StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:nil target:self action:@selector(onCategoryAdded:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
		else
		{
			currentCategory = indexPath.row / 2;

			StringChoiceController *ctrl = [[StringChoiceController alloc] initWithPlaceholder:_("Enter category name") text:[(Category *)[categories objectAtIndex:currentCategory] name] target:self action:@selector(onCategoryChanged:)];
			[self.navigationController presentModalViewController:ctrl animated:YES];
			[ctrl release];
		}
	}
	else
	{
		TaskViewController *ctrl;
	
		if (indexPath.row)
		{
			ctrl = [[TaskViewController alloc] initWithTitle:[[categories objectAtIndex:indexPath.row - 1] name] category:[[categories objectAtIndex:indexPath.row - 1] objectId] categoryController:self parentTask:nil edit:NO];
		}
		else
		{
			ctrl = [[TaskViewController alloc] initWithTitle:_("All") category:-1 categoryController:self parentTask:nil edit:NO];
		}
	
		[[PositionStore instance] push:self indexPath:indexPath type:TYPE_DETAILS];
	
		[self.navigationController pushViewController:ctrl animated:YES];
		[ctrl release];
	}
}

- (void)onCategoryChanged:(NSString *)name
{
	if (name != nil)
	{
		Category *category = [categories objectAtIndex:currentCategory];
		
		category.name = name;
		[category save];
	}

	[self.tableView reloadData];
	[self.navigationController dismissModalViewControllerAnimated:YES];
	[self.tableView deselectRowAtIndexPath:[self.tableView indexPathForSelectedRow] animated:NO];
}

- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath
{
	BadgedCell *cell;

	if (self.editing)
	{
		Category *category = [categories objectAtIndex:indexPath.row / 2];
		
		if (indexPath.row % 2)
		{
			static NSString *CellIdentifier = @"BadgedCell";

			cell = (BadgedCell *)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
			if (cell == nil)
			{
				cell = [[[CellFactory cellFactory] createBadgedCell] autorelease];
			}

			cell.textLabel.text = _("Add subcategory");
			cell.textLabel.textColor = [UIColor grayColor];
			[cell.badge clearAnnotations];
			cell.badge.text = nil;

			cell.indentationLevel = category.level + 1;
		}
		else
		{
			cell = (BadgedCell *)[super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row / 2 inSection:indexPath.section]];
		}
	}
	else
	{
		if (indexPath.row)
		{
			cell = (BadgedCell *)[super tableView:tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:indexPath.row - 1 inSection:indexPath.section]];
		}
		else
		{
			static NSString *CellIdentifier = @"BadgedCell";
			
			cell = (BadgedCell *)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
			if (cell == nil)
			{
				cell = [[[CellFactory cellFactory] createBadgedCell] autorelease];
			}
			
			[cell.badge clearAnnotations];

			cell.textLabel.text = _("All");

			[[[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM AllTask WHERE completionDate IS NULL AND parentId IS NULL"] execWithTarget:self action:@selector(onGotTotal:)];
			cell.badge.text = [NSString stringWithFormat:@"%d", totalCount];
			cell.badge.capsuleColor = [UIColor blackColor];
			[[[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM NotStartedTask WHERE completionDate IS NULL AND parentId IS NULL"] execWithTarget:self action:@selector(onGotTotal:)];
			if (totalCount)
				[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", totalCount] capsuleColor:[UIColor grayColor]];
			[[[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM StartedTask WHERE completionDate IS NULL AND parentId IS NULL"] execWithTarget:self action:@selector(onGotTotal:)];
			if (totalCount)
				[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", totalCount] capsuleColor:[UIColor blueColor]];
			[[[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM DueSoonTask WHERE completionDate IS NULL AND parentId IS NULL"] execWithTarget:self action:@selector(onGotTotal:)];
			if (totalCount)
				[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", totalCount] capsuleColor:[UIColor orangeColor]];
			[[[Database connection] statementWithSQL:@"SELECT COUNT(*) AS total FROM OverdueTask WHERE completionDate IS NULL AND parentId IS NULL"] execWithTarget:self action:@selector(onGotTotal:)];
			if (totalCount)
				[cell.badge addAnnotation:[NSString stringWithFormat:@"%d", totalCount] capsuleColor:[UIColor redColor]];
			
			cell.indentationLevel = 0;
		}

		cell.textLabel.textColor = [UIColor blackColor];
	}

	cell.accessoryType = UITableViewCellAccessoryDisclosureIndicator;
	
	[cell layoutSubviews];

	return cell;
}

- (void)onGotTotal:(NSDictionary *)dict
{
	totalCount = [[dict objectForKey:@"total"] intValue];
}

//===========================================================

- (IBAction)onSynchronize:(UIBarButtonItem *)button
{
	button.enabled = NO;

	if (![Configuration configuration].name)
	{
		// Name/domain not defined, browse
		BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
		browser.delegate = self;
		browser.searchingForServicesString = _("Looking for Task Coach");
		[self.navigationController presentModalViewController:browser animated:YES];
		[browser release];
	}
	else
	{
		NSNetService *srv = [[NSNetService alloc] initWithDomain:[Configuration configuration].domain type:@"_taskcoachsync._tcp" name:[Configuration configuration].name];
		srv.delegate = self;
		[srv resolveWithTimeout:5];
	}
}

- (UITableViewCellEditingStyle)tableView:(UITableView *)tableView editingStyleForRowAtIndexPath:(NSIndexPath *)indexPath
{
	return (indexPath.row % 2) ? UITableViewCellEditingStyleInsert : UITableViewCellEditingStyleDelete;
}

// NSNetService delegate

- (void)netService:(NSNetService *)sender didNotResolve:(NSDictionary *)errorDict
{
	// Browse again...

	BonjourBrowser *browser = [[BonjourBrowser alloc] initForType:@"_taskcoachsync._tcp" inDomain:@"local." customDomains:nil showDisclosureIndicators:NO showCancelButton:YES];
	browser.delegate = self;
	browser.searchingForServicesString = _("Looking for Task Coach");
	[self.navigationController presentModalViewController:browser animated:YES];
	[browser release];
	[sender release];
}

- (void)netServiceDidResolveAddress:(NSNetService *)sender
{
	SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[sender hostName] port:[sender port]];
	[self.navigationController presentModalViewController:ctrl animated:YES];
	[ctrl release];
}

- (void)onSyncFinished
{
	[self loadCategories];
	[self.tableView reloadData];
	[self.navigationController dismissModalViewControllerAnimated:YES];
	syncButton.enabled = YES;
	fileButton.enabled = ([Database connection].fileNumber >= 2);
}

- (void)bonjourBrowser:(BonjourBrowser*)browser didResolveInstance:(NSNetService*)ref
{
	if (ref)
	{
		NSLog(@"Found Task Coach: %@:%d", [ref hostName], [ref port]);

		[Configuration configuration].domain = [ref domain];
		[Configuration configuration].name = [ref name];
		[[Configuration configuration] save];

		SyncViewController *ctrl = [[SyncViewController alloc] initWithTarget:self action:@selector(onSyncFinished) host:[ref hostName] port:[ref port]];
		[self.navigationController.modalViewController presentModalViewController:ctrl animated:YES];
		[ctrl release];
	}
	else
	{
		syncButton.enabled = YES;
		[self.navigationController dismissModalViewControllerAnimated:YES];
	}
}

@end

