//
//  BadgedCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/10/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "BadgeView.h"

@interface BadgedCell : UITableViewCell
{
	BadgeView *badge;
	UILabel *textLabel;
	UIImage *bgImage;
}

@property (nonatomic, retain) IBOutlet BadgeView *badge;
@property (nonatomic, retain) IBOutlet UILabel *textLabel;

@end
